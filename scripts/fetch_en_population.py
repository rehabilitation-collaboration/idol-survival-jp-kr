"""en.wikipedia からグループ母集団を取得する (Phase 3)。

韓国側の主分析と、日韓を同一ソースで比べる感度分析の両方に使う。

    python3 scripts/fetch_en_population.py kr    # 韓国 (主分析)
    python3 scripts/fetch_en_population.py jp    # 日本 (英語版による対称化)

韓国語版には年別の結成/解散カテゴリが無いため、韓国の主分析は英語版を使う。
日本は日本語版が主分析だが、**言語版によるカバー率の差が日韓比較を歪める**ため、
同じ英語版で揃えた母集団でも推定して頑健性を確認する (PLAN の二層設計)。

途中で止まっても再実行すれば続きから取る。出力は data/raw/ 配下 (git 管理外)。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (en.wikipedia population fetch; contact via GitHub repo)"
API = "https://en.wikipedia.org/w/api.php"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
BATCH = 20

# 実測でメンバーを持つカテゴリのみ (K-pop girl groups / boy bands は 0 件だった)。
# South Korean idol groups は 20 件 + boy bands / girl groups をサブカテゴリに持つ
TARGETS = {
    "kr": [
        "K-pop music groups",
        "South Korean idol groups",
        "South Korean boy bands",
        "South Korean girl groups",
    ],
    "jp": [
        "Japanese idol groups",
        "Japanese girl groups",
        "Japanese boy bands",
        "J-pop music groups",
    ],
}


def api_get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
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


def category_members(cat):
    out, cont = [], {}
    while True:
        d = api_get({
            "action": "query", "list": "categorymembers",
            "cmtitle": f"Category:{cat}", "cmlimit": "500",
            "cmtype": "page", "cmnamespace": "0", **cont,
        })
        out += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        if "continue" not in d:
            return out
        cont = {"cmcontinue": d["continue"]["cmcontinue"]}
        time.sleep(0.3)


def build_seed(country, seed_path):
    if os.path.exists(seed_path):
        with open(seed_path, encoding="utf-8") as f:
            seed = json.load(f)
        print(f"既存シードを使用: {sum(len(v) for v in seed.values())} 件 (重複込み)")
        return seed
    seed = {}
    for cat in TARGETS[country]:
        try:
            seed[cat] = category_members(cat)
        except urllib.error.HTTPError as e:
            print(f"  {cat}: 取得失敗 ({e.code}) — 存在しないカテゴリとして扱う")
            seed[cat] = []
            continue
        print(f"  {cat}: {len(seed[cat])} 件", flush=True)
        time.sleep(0.3)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False)
    return seed


def fetch_pages(titles, pages_path):
    done = set()
    if os.path.exists(pages_path):
        with open(pages_path, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["title"])
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"取得済み {len(done)} 件をスキップ")

    todo = [t for t in titles if t not in done]
    print(f"取得対象 {len(todo)} 件 / 全 {len(titles)} 件")
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(pages_path, "a", encoding="utf-8") as out:
        for i in range(0, len(todo), BATCH):
            chunk = todo[i : i + BATCH]
            d = api_get({
                "action": "query", "titles": "|".join(chunk),
                "prop": "extracts|categories|revisions",
                "exintro": "1", "explaintext": "1", "exlimit": str(BATCH),
                "cllimit": "500", "rvprop": "content", "rvslots": "main",
                "redirects": "1",
            })
            q = d.get("query", {})
            redirects = {r["to"]: r["from"] for r in q.get("redirects", [])}
            got = set()
            for p in q.get("pages", {}).values():
                if "missing" in p:
                    continue
                try:
                    wt = p["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    wt = ""
                rec = {
                    "title": p["title"],
                    "requested_as": redirects.get(p["title"]),
                    "categories": [c["title"].split(":", 1)[-1] for c in p.get("categories", [])],
                    "lead": (p.get("extract") or "").strip(),
                    "wikitext": wt,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                got.add(p["title"])
                if rec["requested_as"]:
                    got.add(rec["requested_as"])
            for t in chunk:
                if t not in got:
                    out.write(json.dumps({"title": t, "missing": True}, ensure_ascii=False) + "\n")
            out.flush()
            n = i + len(chunk)
            if (i // BATCH) % 5 == 0 or n >= len(todo):
                print(f"  {n}/{len(todo)}", flush=True)
            time.sleep(0.2)


def main():
    country = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if country not in TARGETS:
        print(f"usage: python3 scripts/fetch_en_population.py {{{'|'.join(TARGETS)}}}")
        return 1
    pages_path = os.path.join(OUT_DIR, f"en_{country}_pages.jsonl")
    seed_path = os.path.join(OUT_DIR, f"en_{country}_seed.json")

    seed = build_seed(country, seed_path)
    titles = sorted({t for v in seed.values() for t in v})
    print(f"\nシード和集合: {len(titles)} 件")
    fetch_pages(titles, pages_path)
    print(f"\n完了: {pages_path}")


if __name__ == "__main__":
    sys.exit(main())
