"""韓国側の母集団を en.wikipedia から作れるかを実測する。

韓国語版には年別の結成/解散カテゴリが存在しない (Phase 0 実測) ため、
韓国側は英語版を使う。英語版で何が取れるかを、母集団を作る前に確かめる:

    1. K-pop 関連カテゴリの構造とサイズ (サブカテゴリを含むか)
    2. 年別カテゴリ (Musical groups established/disestablished in YYYY) の付与率
    3. Infobox years_active の保有率とパース可能性
    4. 冒頭定義文の形 (日本語版と同じ手が使えるか)

    python3 scripts/probe_kr_source.py

★ Kim (2026) の母集団は 1,182 組。英語版がその何割を捉えるかが
   そのまま手法のカバー率になる。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (kr source probe)"
API = "https://en.wikipedia.org/w/api.php"

SEED_CATEGORIES = [
    "K-pop music groups",
    "South Korean idol groups",
    "South Korean boy bands",
    "South Korean girl groups",
    "South Korean musical groups",
    "K-pop girl groups",
    "K-pop boy bands",
]

YEAR_EST = re.compile(r"^Musical groups established in (\d{4})$")
YEAR_DIS = re.compile(r"^Musical groups disestablished in (\d{4})$")


def api_get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
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


def category_members(cat, cmtype="page"):
    out, cont = [], {}
    while True:
        d = api_get({
            "action": "query", "list": "categorymembers",
            "cmtitle": f"Category:{cat}", "cmlimit": "500",
            "cmtype": cmtype, **cont,
        })
        out += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        if "continue" not in d:
            return out
        cont = {"cmcontinue": d["continue"]["cmcontinue"]}
        time.sleep(0.3)


def fetch_pages(titles):
    out = {}
    for i in range(0, len(titles), 20):
        d = api_get({
            "action": "query", "titles": "|".join(titles[i : i + 20]),
            "prop": "extracts|categories|revisions",
            "exintro": "1", "explaintext": "1", "exlimit": "20",
            "cllimit": "500", "rvprop": "content", "rvslots": "main",
            "redirects": "1",
        })
        for p in d.get("query", {}).get("pages", {}).values():
            if "missing" in p:
                continue
            try:
                wt = p["revisions"][0]["slots"]["main"]["*"]
            except (KeyError, IndexError):
                wt = ""
            out[p["title"]] = {
                "categories": [c["title"].split(":", 1)[-1] for c in p.get("categories", [])],
                "lead": (p.get("extract") or "").strip(),
                "wikitext": wt,
            }
        time.sleep(0.3)
    return out


def main():
    print("=== 1. シードカテゴリのサイズとサブカテゴリ ===")
    all_members = set()
    for cat in SEED_CATEGORIES:
        try:
            pages = category_members(cat, "page")
            subs = category_members(cat, "subcat")
        except urllib.error.HTTPError as e:
            print(f"  {cat}: 取得失敗 ({e.code})")
            continue
        all_members |= set(pages)
        print(f"  {cat}: 記事 {len(pages)} / サブカテゴリ {len(subs)}")
        for s in subs[:6]:
            print(f"      - {s}")
        time.sleep(0.3)

    print(f"\n  シード和集合 (サブカテゴリ未展開): {len(all_members)} 件")
    print(f"  ※ Kim (2026) の母集団は 1,182 組")

    sample = sorted(all_members)[:150]
    print(f"\n=== 2. サンプル {len(sample)} 件で取得可能性を測る ===")
    pages = fetch_pages(sample)
    n = len(pages) or 1
    print(f"  取得成功: {len(pages)} 件")

    est = dis = both_cat = 0
    ya_field = 0
    lead_year = 0
    lead_kr = 0
    examples = []
    for title, p in pages.items():
        cats = p["categories"]
        e = [m.group(1) for c in cats if (m := YEAR_EST.match(c))]
        d = [m.group(1) for c in cats if (m := YEAR_DIS.match(c))]
        est += bool(e)
        dis += bool(d)
        if e and d:
            both_cat += 1
        if re.search(r"\|\s*years_active\s*=", p["wikitext"], re.I):
            ya_field += 1
        lead = p["lead"]
        if re.search(r"\b(19|20)\d{2}\b", lead[:300]):
            lead_year += 1
        if re.search(r"South Korean|Korean", lead[:300]):
            lead_kr += 1
        if len(examples) < 12:
            first = re.split(r"(?<=[.])\s", lead.replace("\n", " "))[0] if lead else ""
            examples.append((title, e[0] if e else "-", d[0] if d else "-", first[:110]))

    print(f"\n--- カテゴリ由来の年 ---")
    print(f"  established in YYYY あり : {est}/{n} ({est/n:.1%})")
    print(f"  disestablished in YYYY あり: {dis}/{n} ({dis/n:.1%})")
    print(f"  両方あり                  : {both_cat}/{n} ({both_cat/n:.1%})")
    print(f"\n--- Infobox / リード文 ---")
    print(f"  years_active フィールドあり: {ya_field}/{n} ({ya_field/n:.1%})")
    print(f"  リード文に 4 桁年あり      : {lead_year}/{n} ({lead_year/n:.1%})")
    print(f"  リード文に Korean 表記あり : {lead_kr}/{n} ({lead_kr/n:.1%})")

    print(f"\n--- 冒頭定義文の例 ---")
    for t, e, d, s in examples:
        print(f"  [{e}-{d}] {t[:30]}")
        print(f"          {s}")


if __name__ == "__main__":
    sys.exit(main())
