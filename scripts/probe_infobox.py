"""日本語Wikipedia本文のInfoboxから活動期間が取れるかを実測する。

Wikidata(P571/P576)がカバー率13%/1%で使えないと判明したため、
代替ソースとして記事wikitextのInfoboxを検証する。
"""
import json
import re
import time
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (feasibility probe)"
SAMPLE_LIMIT = 120

# Infobox Musician の活動期間フィールド。表記ゆれを許容する。
ACTIVE_FIELD = re.compile(r"^\s*\|\s*(活動期間|活動年数|Years_active|years_active)\s*=\s*(.*)$", re.M)
# 「2010年」「2010年4月」「2010-04-01」等から西暦4桁を拾う
YEAR = re.compile(r"(19[5-9]\d|20[0-4]\d)")


def api_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def category_members(category, limit):
    titles, cont = [], ""
    enc = urllib.parse.quote(category)
    while len(titles) < limit:
        d = api_get(
            f"https://ja.wikipedia.org/w/api.php?action=query&list=categorymembers"
            f"&cmtitle=Category:{enc}&cmlimit=500&cmtype=page&format=json{cont}"
        )
        titles += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        c = d.get("continue", {}).get("cmcontinue", "")
        if not c:
            break
        cont = f"&cmcontinue={urllib.parse.quote(c)}"
    return titles[:limit]


def fetch_wikitext(titles):
    out = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i : i + 20]
        q = urllib.parse.quote("|".join(chunk))
        d = api_get(
            f"https://ja.wikipedia.org/w/api.php?action=query&titles={q}"
            f"&prop=revisions&rvprop=content&rvslots=main&format=json"
        )
        for p in d["query"]["pages"].values():
            try:
                out[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
            except (KeyError, IndexError):
                pass
        time.sleep(0.8)
    return out


def classify(raw):
    """活動期間フィールドの中身から (開始年, 終了年, 現役か) を判定する。"""
    years = YEAR.findall(raw)
    if not years:
        return None, None, None
    start = int(years[0])
    ongoing = bool(re.search(r"現在|-\s*$|‐\s*$|–\s*$|〜\s*$|～\s*$", raw.strip()))
    end = int(years[-1]) if len(years) > 1 and not ongoing else None
    return start, end, ongoing


def main():
    for cat in ["日本の女性アイドルグループ", "日本の男性アイドルグループ"]:
        titles = category_members(cat, SAMPLE_LIMIT)
        texts = fetch_wikitext(titles)

        n = len(titles)
        has_field, parsed_start, parsed_end, ongoing_n = 0, 0, 0, 0
        samples = []
        for t, wt in texts.items():
            m = ACTIVE_FIELD.search(wt)
            if not m:
                continue
            has_field += 1
            raw = m.group(2).strip()
            s, e, og = classify(raw)
            if s:
                parsed_start += 1
            if e:
                parsed_end += 1
            if og:
                ongoing_n += 1
            if len(samples) < 6:
                samples.append((t, raw[:60], s, e, og))

        print(f"\n=== {cat} (sample {n}, wikitext取得 {len(texts)}) ===")
        print(f"  活動期間フィールドあり: {has_field}/{n} ({has_field/n:.1%})")
        print(f"  開始年パース成功      : {parsed_start}/{n} ({parsed_start/n:.1%})")
        print(f"  終了年パース成功      : {parsed_end}/{n} ({parsed_end/n:.1%})")
        print(f"  現役(打ち切り)判定    : {ongoing_n}/{n} ({ongoing_n/n:.1%})")
        for t, raw, s, e, og in samples:
            print(f"    - {t}: raw={raw!r} -> start={s} end={e} ongoing={og}")


if __name__ == "__main__":
    main()
