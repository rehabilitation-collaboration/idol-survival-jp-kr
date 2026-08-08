"""記事冒頭の定義文からアイドル判定できるかを実測する。

カテゴリ (L1) は ground truth の 46% しか拾えず、旧ジャニーズ系と LDH 系が
構造的に全滅する (probe_idol_detection.py で実測)。事務所リストを
「L1 陽性の事務所」から導出する案は、この偏りのせいで循環する。

代替として、Wikipedia 記事の冒頭定義文 (lead sentence) を使えるかを測る。
日本語版には「〇〇は、日本の男性アイドルグループ。」のように
冒頭で種別を定義する強い編集慣行があり、カテゴリより網羅的な可能性がある。
国籍 (韓国の) や種別 (バンド/声優ユニット) も同じ文に出るため、
除外規則も同一ソースから作れる。

    python3 scripts/probe_lead_definition.py

出力: ground truth に対する lead 判定のカバー率と、L1 との一致/不一致。
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from probe_idol_detection import GROUND_TRUTH, IDOL_CATEGORIES

UA = "IdolSurvivalResearch/0.1 (lead sentence probe)"

# 冒頭定義文から拾うシグナル。順序は判定の優先度ではなく表示順。
IDOL_PAT = re.compile(r"アイドル")
GIRL_BOY_PAT = re.compile(r"ガールズ(グループ|ユニット)|ボーイズ(グループ|ユニット)|男性グループ|女性グループ")
KR_PAT = re.compile(r"韓国|大韓民国|K-POP|Kポップ")
BAND_PAT = re.compile(r"ロックバンド|バンド")
SEIYU_PAT = re.compile(r"声優")
GROUP_PAT = re.compile(r"(音楽|ダンス|ヴォーカル|ボーカル|コーラス)?(グループ|ユニット|デュオ|トリオ)")
# 「アイドル」と名乗らないがアイドル産業に属する疑いが濃い自称。
# LDH 系が一貫して使う「ダンス&ボーカルグループ」がこの代表。
# 含めるか否かは母集団定義の判断事項なので、独立に計測する。
DANCE_VOCAL_PAT = re.compile(
    r"ダンス\s*[&＆・]\s*ヴ?[ォボ]ーカル|ダンスボーカル|パフォーマンスグループ"
)


def api_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(6 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_lead(titles):
    """タイトル -> (冒頭プレーンテキスト, カテゴリ集合)。リダイレクトは追う。"""
    out, redirects = {}, {}
    for i in range(0, len(titles), 20):
        q = urllib.parse.quote("|".join(titles[i : i + 20]))
        d = api_get(
            f"https://ja.wikipedia.org/w/api.php?action=query&titles={q}"
            f"&prop=extracts|categories&exintro=1&explaintext=1&exlimit=20"
            f"&cllimit=500&redirects=1&format=json"
        )
        q_ = d.get("query", {})
        for r in q_.get("redirects", []):
            redirects[r["to"]] = r["from"]
        for p in q_.get("pages", {}).values():
            if "missing" in p:
                out[p["title"]] = None
                continue
            cats = {c["title"].split(":", 1)[-1] for c in p.get("categories", [])}
            out[p["title"]] = {
                "lead": (p.get("extract") or "").strip(),
                "categories": cats,
                "redirected_from": redirects.get(p["title"]),
            }
        time.sleep(1.0)
    return out


def first_sentence(text):
    """冒頭の定義文を取り出す。

    素朴に最初の句点で切ると、記事名に句点を含むグループ (モーニング娘。)
    で「モーニング娘。」だけになって述部が消える。定義文は「〜は、」で
    始まる強い慣行があるので、まず述部側を探し、無ければ先頭 150 字に落とす。
    """
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"は[、,](.{0,200}?[。])", text)
    if m:
        return m.group(0).strip()
    m = re.search(r"^(.{0,300}?[。])", text)
    return (m.group(1) if m else text[:200]).strip()


def classify(lead):
    """冒頭定義文から拾えるシグナルを返す。"""
    s = first_sentence(lead)
    return {
        "idol": bool(IDOL_PAT.search(s)),
        "girl_boy": bool(GIRL_BOY_PAT.search(s)),
        "kr": bool(KR_PAT.search(s)),
        "band": bool(BAND_PAT.search(s)),
        "seiyu": bool(SEIYU_PAT.search(s)),
        "group": bool(GROUP_PAT.search(s)),
        "dance_vocal": bool(DANCE_VOCAL_PAT.search(s)),
        "sentence": s,
    }


def main():
    titles = [t for g in GROUND_TRUTH.values() for t in g]
    print(f"ground truth {len(titles)} 件の冒頭定義文を取得中...\n")
    pages = fetch_lead(titles)
    by_request = {}
    for title, data in pages.items():
        if data and data["redirected_from"]:
            by_request[data["redirected_from"]] = title
        by_request.setdefault(title, title)

    stats = {"n": 0, "lead_idol": 0, "l1": 0, "both": 0, "lead_only": 0, "l1_only": 0, "neither": 0}
    rows = []

    for bucket, group in GROUND_TRUTH.items():
        print(f"=== {bucket} ===")
        for t in group:
            data = pages.get(by_request.get(t, t))
            if data is None:
                print(f"  {t}: 記事なし")
                continue
            c = classify(data["lead"])
            l1 = bool(data["categories"] & IDOL_CATEGORIES)
            stats["n"] += 1
            stats["lead_idol"] += c["idol"]
            stats["l1"] += l1
            if c["idol"] and l1:
                stats["both"] += 1
            elif c["idol"]:
                stats["lead_only"] += 1
            elif l1:
                stats["l1_only"] += 1
            else:
                stats["neither"] += 1
            rows.append((bucket, t, c, l1))

            flags = "".join(
                [
                    "I" if c["idol"] else "-",
                    "G" if c["girl_boy"] else "-",
                    "D" if c["dance_vocal"] else "-",
                    "K" if c["kr"] else "-",
                    "B" if c["band"] else "-",
                    "S" if c["seiyu"] else "-",
                ]
            )
            print(f"  [{flags}] L1={'○' if l1 else '×'} {t}")
            print(f"        {c['sentence'][:120]}")
        print()

    n = stats["n"] or 1
    print("=" * 70)
    print("フラグ凡例: I=アイドル G=ガールズ/ボーイズ D=ダンス&ボーカル K=韓国 B=バンド S=声優\n")
    print(f"ground truth 総数 (記事あり): {stats['n']}")
    print(f"  冒頭定義文に「アイドル」   : {stats['lead_idol']:>3} ({stats['lead_idol']/n:.1%})")
    print(f"  L1 カテゴリで陽性          : {stats['l1']:>3} ({stats['l1']/n:.1%})")
    print(f"  両方で陽性 (一致)          : {stats['both']:>3}")
    print(f"  冒頭のみ (L1 が漏らした)   : {stats['lead_only']:>3}")
    print(f"  L1 のみ (冒頭が漏らした)   : {stats['l1_only']:>3}")
    print(f"  どちらも陰性               : {stats['neither']:>3}")

    # 判定ルール候補ごとのカバー率。ground truth は全て「アイドルであることに
    # 争いがない」+「境界事例」なので、境界を除いた再現率が本命の指標になる。
    core = [r for r in rows if not r[0].startswith("境界事例")]
    print("\n--- 判定ルール候補のカバー率 ---")
    for label, fn in [
        ("A: L1 のみ", lambda c, l1: l1),
        ("B: lead「アイドル」のみ", lambda c, l1: c["idol"]),
        ("C: A OR B", lambda c, l1: l1 or c["idol"]),
        ("D: C OR ダンス&ボーカル", lambda c, l1: l1 or c["idol"] or c["dance_vocal"]),
        (
            "E: D OR ガールズ/ボーイズ",
            lambda c, l1: l1 or c["idol"] or c["dance_vocal"] or c["girl_boy"],
        ),
    ]:
        allh = sum(1 for _, _, c, l1 in rows if fn(c, l1))
        coreh = sum(1 for _, _, c, l1 in core if fn(c, l1))
        kr = sum(1 for _, _, c, l1 in rows if fn(c, l1) and c["kr"])
        print(
            f"  {label:<26} 中核 {coreh:>3}/{len(core)} ({coreh/len(core):.1%})"
            f"   全体 {allh:>3}/{n}   うち韓国グループ混入 {kr}"
        )

    print(f"\n--- 中核 ground truth で「C: L1 OR lead」でも拾えなかった ---")
    for bucket, t, c, l1 in core:
        if not (c["idol"] or l1):
            print(f"  [{bucket}] {t}  D={'○' if c['dance_vocal'] else '×'}")
            print(f"      {c['sentence'][:110]}")

    print("\n--- 除外シグナルの効き方 (K-POP / バンド / 声優) ---")
    for key, label in [("kr", "韓国"), ("band", "バンド"), ("seiyu", "声優")]:
        hit = [t for _, t, c, _ in rows if c[key]]
        print(f"  {label}: {len(hit)} 件  {', '.join(hit[:14])}")


if __name__ == "__main__":
    main()
