"""日本側の母集団候補を ja.wikipedia から全件取得してローカルに保存する。

母集団の主軸は「YYYY年に結成した音楽グループ」カテゴリ (1996-2025)。
アイドル系カテゴリを主軸にしないのは、旧ジャニーズ系がそこに
一切入っていないため (probe_idol_detection.py で実測: L1 単独の再現率 51.9%)。

判定に必要なものを 1 記事 1 行の JSONL で保存する:
    title / categories / lead (冒頭プレーンテキスト) / wikitext

    python3 scripts/fetch_jp_population.py

途中で止まっても再実行すれば続きから取る (取得済みタイトルはスキップ)。
出力は data/raw/ 配下 (git 管理外・数百 MB)。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (population fetch; contact via GitHub repo)"
YEARS = list(range(1996, 2026))
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PAGES_PATH = os.path.join(OUT_DIR, "ja_pages.jsonl")
INDEX_PATH = os.path.join(OUT_DIR, "ja_category_index.json")
BATCH = 20  # extracts の exlimit 上限


def api_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if (code is not None and code not in (429, 500, 502, 503, 504)) or attempt == 5:
                raise
            time.sleep(6 * (attempt + 1))
    raise RuntimeError("unreachable")


def category_members(category):
    """カテゴリの全メンバー (通常記事のみ) を返す。"""
    titles, cont = [], ""
    enc = urllib.parse.quote(category)
    while True:
        d = api_get(
            f"https://ja.wikipedia.org/w/api.php?action=query&list=categorymembers"
            f"&cmtitle=Category:{enc}&cmlimit=500&cmtype=page&cmnamespace=0"
            f"&format=json{cont}"
        )
        titles += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        c = d.get("continue", {}).get("cmcontinue", "")
        if not c:
            return titles
        cont = f"&cmcontinue={urllib.parse.quote(c)}"
        time.sleep(0.5)


def build_index():
    """年別カテゴリのメンバー一覧。結成年と解散年をカテゴリ由来で確定させる。"""
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding="utf-8") as f:
            idx = json.load(f)
        print(f"既存インデックスを使用: {INDEX_PATH}")
        return idx

    idx = {"formed": {}, "dissolved": {}}
    for kind, tpl in [
        ("formed", "{y}年に結成した音楽グループ"),
        ("dissolved", "{y}年に解散した音楽グループ"),
    ]:
        for y in YEARS:
            members = category_members(tpl.format(y=y))
            idx[kind][str(y)] = members
            print(f"  [{kind}] {y}: {len(members)} 件", flush=True)
            time.sleep(0.5)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False)
    return idx


def fetch_pages(titles):
    """未取得タイトルの本文・カテゴリ・冒頭文を取り、JSONL に追記する。"""
    done = set()
    if os.path.exists(PAGES_PATH):
        with open(PAGES_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["title"])
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"取得済み {len(done)} 件をスキップ")

    todo = [t for t in titles if t not in done]
    print(f"取得対象 {len(todo)} 件 / 全 {len(titles)} 件")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PAGES_PATH, "a", encoding="utf-8") as out:
        for i in range(0, len(todo), BATCH):
            chunk = todo[i : i + BATCH]
            q = urllib.parse.quote("|".join(chunk))
            d = api_get(
                f"https://ja.wikipedia.org/w/api.php?action=query&titles={q}"
                f"&prop=extracts|categories|revisions"
                f"&exintro=1&explaintext=1&exlimit={BATCH}"
                f"&cllimit=500&rvprop=content&rvslots=main"
                f"&redirects=1&format=json"
            )
            q_ = d.get("query", {})
            # リダイレクトされた場合、要求タイトルも残して名寄せできるようにする
            redirects = {r["to"]: r["from"] for r in q_.get("redirects", [])}
            got = set()
            for p in q_.get("pages", {}).values():
                if "missing" in p:
                    continue
                try:
                    wt = p["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    wt = ""
                rec = {
                    "title": p["title"],
                    "requested_as": redirects.get(p["title"]),
                    "categories": [
                        c["title"].split(":", 1)[-1] for c in p.get("categories", [])
                    ],
                    "lead": (p.get("extract") or "").strip(),
                    "wikitext": wt,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                got.add(p["title"])
                if rec["requested_as"]:
                    got.add(rec["requested_as"])
            # リダイレクト解決で別名になった分も「済」として記録し、再取得を防ぐ
            for t in chunk:
                if t not in got:
                    out.write(
                        json.dumps({"title": t, "missing": True}, ensure_ascii=False) + "\n"
                    )
            out.flush()
            n = i + len(chunk)
            if (i // BATCH) % 10 == 0 or n >= len(todo):
                print(f"  {n}/{len(todo)}", flush=True)
            # 1 バッチのレスポンス自体が 1 秒以上かかるので、これで
            # 実効 1 req/s 未満に収まる。429 はリトライで待つ
            time.sleep(0.2)


def main():
    idx = build_index()
    titles = sorted(
        {t for members in idx["formed"].values() for t in members}
        | {t for members in idx["dissolved"].values() for t in members}
    )
    print(f"\n結成/解散カテゴリの和集合: {len(titles)} 件")
    fetch_pages(titles)
    print(f"\n完了: {PAGES_PATH}")


if __name__ == "__main__":
    sys.exit(main())
