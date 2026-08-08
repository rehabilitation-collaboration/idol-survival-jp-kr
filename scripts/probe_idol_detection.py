"""アイドル判定レイヤーの取りこぼしを ground truth で実測する。

Phase 1 の判定ルールを確定させるための設計根拠。
「L1 (アイドル系カテゴリ所属) だけでは何が漏れるか」「Infobox 事務所は
判定に使える粒度で書かれているか」を、誰が見てもアイドルと言える
既知グループの集合に対して測る。

    python3 scripts/probe_idol_detection.py

ground truth は判定ルールではなく検証用の正解セット。
事務所別に代表グループを並べてあるので、特定事務所だけ漏れる
(旧ジャニーズ/STARTO 系が疑われる) 構造を検出できる。
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (idol detection ground truth)"

# 検証用 ground truth。「アイドルであることに争いがない」グループを事務所別に列挙。
# 判定ルールではない (これを母集団定義に使うと恣意的になる)。
GROUND_TRUTH = {
    "STARTO/旧ジャニーズ": [
        "嵐 (グループ)", "SMAP", "TOKIO", "V6 (グループ)", "KinKi Kids", "NEWS (グループ)",
        "関ジャニ∞", "KAT-TUN", "Hey! Say! JUMP", "Kis-My-Ft2", "Sexy Zone",
        "King & Prince", "SixTONES", "Snow Man", "なにわ男子", "光GENJI", "少年隊",
    ],
    "秋元康系": [
        "AKB48", "SKE48", "NMB48", "HKT48", "NGT48", "STU48",
        "乃木坂46", "櫻坂46", "日向坂46", "おニャン子クラブ",
    ],
    "ハロプロ/アップフロント": [
        "モーニング娘。", "Berryz工房", "℃-ute", "アンジュルム", "Juice=Juice",
        "スマイレージ", "つばきファクトリー",
    ],
    "LDH": [
        "EXILE", "三代目 J SOUL BROTHERS", "GENERATIONS from EXILE TRIBE",
        "E-girls", "THE RAMPAGE from EXILE TRIBE", "Happiness (グループ)",
    ],
    "スターダスト": [
        "ももいろクローバーZ", "私立恵比寿中学", "たこやきレインボー", "3B junior",
    ],
    "その他事務所": [
        "Perfume", "BABYMETAL", "でんぱ組.inc", "SPEED", "MAX (音楽グループ)",
        "Little Glee Monster", "東京女子流", "こぶしファクトリー",
    ],
    "境界事例(バンド/声優/K-POP)": [
        "AAA (音楽グループ)", "いきものがかり", "ゆず (音楽グループ)",
        "スフィア (声優ユニット)", "Μ's", "Aqours",
        "TWICE", "KARA", "少女時代", "東方神起", "2PM", "2NE1",
    ],
}

# アイドル系カテゴリ (L1)。ja.wikipedia の実カテゴリ名。
IDOL_CATEGORIES = {
    "日本の女性アイドルグループ",
    "日本の男性アイドルグループ",
    "日本のアイドルグループ",
    "アイドルグループ",
}

FIELD_VALUE = re.compile(
    r"^\s*\|\s*(事務所|Production|production|所属事務所)\s*=\s*(.*)$", re.M
)
GENRE_VALUE = re.compile(r"^\s*\|\s*(ジャンル|Genre|genre)\s*=\s*(.*)$", re.M)
YEAR_FORMED_CAT = re.compile(r"^(\d{4})年に結成した音楽グループ$")


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


def fetch(titles):
    """タイトル -> {categories, wikitext, redirected_from}。リダイレクトは追う。"""
    out = {}
    redirects = {}
    for i in range(0, len(titles), 20):
        q = urllib.parse.quote("|".join(titles[i : i + 20]))
        d = api_get(
            f"https://ja.wikipedia.org/w/api.php?action=query&titles={q}"
            f"&prop=categories|revisions&cllimit=500&rvprop=content&rvslots=main"
            f"&redirects=1&format=json"
        )
        q_ = d.get("query", {})
        for r in q_.get("redirects", []):
            redirects[r["to"]] = r["from"]
        for p in q_.get("pages", {}).values():
            if "missing" in p:
                out[p["title"]] = None
                continue
            cats = [c["title"].split(":", 1)[-1] for c in p.get("categories", [])]
            try:
                wt = p["revisions"][0]["slots"]["main"]["*"]
            except (KeyError, IndexError):
                wt = ""
            out[p["title"]] = {
                "categories": cats,
                "wikitext": wt,
                "redirected_from": redirects.get(p["title"]),
            }
        time.sleep(1.0)
    return out


def clean_value(v):
    """Infobox の値から装飾を落として読める形にする。"""
    v = re.sub(r"<!--.*?-->", "", v)
    v = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", v, flags=re.S)
    v = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", v)
    v = re.sub(r"\{\{[^}]*\}\}", " ", v)
    v = re.sub(r"<br\s*/?>", " / ", v)
    v = re.sub(r"''+", "", v)
    return re.sub(r"\s+", " ", v).strip(" |")


def first_match(pattern, wt):
    m = pattern.search(wt or "")
    return clean_value(m.group(2)) if m else ""


def main():
    all_titles = [t for group in GROUND_TRUTH.values() for t in group]
    print(f"ground truth {len(all_titles)} 件を取得中...")
    pages = fetch(all_titles)

    # リダイレクト元 -> 実タイトル の逆引き
    by_request = {}
    for title, data in pages.items():
        if data and data["redirected_from"]:
            by_request[data["redirected_from"]] = title
        by_request.setdefault(title, title)

    totals = {"n": 0, "l1": 0, "agency": 0, "genre": 0, "formed_cat": 0}
    l1_missing = []

    for bucket, titles in GROUND_TRUTH.items():
        print(f"\n=== {bucket} ===")
        print(f"{'グループ':<32}{'L1':<5}{'結成cat':<9}{'事務所'}")
        for t in titles:
            actual = by_request.get(t, t)
            data = pages.get(actual)
            if data is None:
                print(f"{t:<32}{'記事なし':<5}")
                continue
            cats = set(data["categories"])
            l1 = bool(cats & IDOL_CATEGORIES)
            years = [
                m.group(1) for c in cats if (m := YEAR_FORMED_CAT.match(c))
            ]
            agency = first_match(FIELD_VALUE, data["wikitext"])
            genre = first_match(GENRE_VALUE, data["wikitext"])

            totals["n"] += 1
            totals["l1"] += l1
            totals["agency"] += bool(agency)
            totals["genre"] += bool(genre)
            totals["formed_cat"] += bool(years)
            if not l1:
                l1_missing.append((bucket, t, agency))

            mark = "○" if l1 else "×"
            yr = years[0] if years else "なし"
            label = t if actual == t else f"{t}→{actual}"
            print(f"{label:<32}{mark:<5}{yr:<9}{agency[:42]}")
            if genre:
                print(f"{'':<32}{'':<5}{'':<9}genre: {genre[:60]}")

    n = totals["n"] or 1
    print("\n" + "=" * 60)
    print(f"ground truth 総数 (記事あり): {totals['n']}")
    print(f"  L1 (アイドル系カテゴリ) で陽性     : {totals['l1']:>3} ({totals['l1']/n:.1%})")
    print(f"  結成年カテゴリに所属               : {totals['formed_cat']:>3} ({totals['formed_cat']/n:.1%})")
    print(f"  Infobox 事務所あり                 : {totals['agency']:>3} ({totals['agency']/n:.1%})")
    print(f"  Infobox ジャンルあり               : {totals['genre']:>3} ({totals['genre']/n:.1%})")

    print(f"\n--- L1 で漏れたグループ ({len(l1_missing)} 件) ---")
    for bucket, t, agency in l1_missing:
        print(f"  [{bucket}] {t}  事務所={agency[:40] or '(なし)'}")


if __name__ == "__main__":
    main()
