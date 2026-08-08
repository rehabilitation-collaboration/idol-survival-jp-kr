"""日本のアイドルグループの結成日/解散日がWikidataでどれだけ埋まっているかを実測する。

母集団リスト構築の実現可能性判定用。カバー率が低ければ設計をやり直す。
"""
import json
import time
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (feasibility probe)"
SAMPLE_LIMIT = 150


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
    """カテゴリ直下の記事タイトルを取得する。"""
    titles = []
    cont = ""
    enc = urllib.parse.quote(category)
    while len(titles) < limit:
        url = (
            f"https://ja.wikipedia.org/w/api.php?action=query&list=categorymembers"
            f"&cmtitle=Category:{enc}&cmlimit=500&cmtype=page&format=json{cont}"
        )
        d = api_get(url)
        titles += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        c = d.get("continue", {}).get("cmcontinue", "")
        if not c:
            break
        cont = f"&cmcontinue={urllib.parse.quote(c)}"
    return titles[:limit]


def wikidata_ids(titles):
    """記事タイトル -> Wikidata Qid。"""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i : i + 50]
        q = urllib.parse.quote("|".join(chunk))
        url = (
            f"https://ja.wikipedia.org/w/api.php?action=query&titles={q}"
            f"&prop=pageprops&ppprop=wikibase_item&format=json"
        )
        for p in api_get(url)["query"]["pages"].values():
            qid = p.get("pageprops", {}).get("wikibase_item")
            if qid:
                out[p["title"]] = qid
        time.sleep(1.2)
    return out


def wikidata_dates(qids):
    """Qid -> {inception: P571, dissolved: P576}。"""
    out = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i : i + 50]
        url = (
            "https://www.wikidata.org/w/api.php?action=wbgetentities&ids="
            + "|".join(chunk)
            + "&props=claims&format=json"
        )
        for qid, ent in api_get(url).get("entities", {}).items():
            claims = ent.get("claims", {})

            def pick(pid):
                for c in claims.get(pid, []):
                    v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                    if isinstance(v, dict) and "time" in v:
                        return v["time"]
                return None

            out[qid] = {"inception": pick("P571"), "dissolved": pick("P576")}
        time.sleep(1.2)
    return out


def main():
    for cat in ["日本の女性アイドルグループ", "日本の男性アイドルグループ"]:
        titles = category_members(cat, SAMPLE_LIMIT)
        qmap = wikidata_ids(titles)
        dates = wikidata_dates(list(qmap.values()))

        n = len(titles)
        linked = len(qmap)
        has_inc = sum(1 for q in qmap.values() if dates.get(q, {}).get("inception"))
        has_dis = sum(1 for q in qmap.values() if dates.get(q, {}).get("dissolved"))

        print(f"\n=== {cat} (sample {n}) ===")
        print(f"  Wikidata紐付き : {linked}/{n} ({linked/n:.1%})")
        print(f"  結成日 P571あり: {has_inc}/{n} ({has_inc/n:.1%})")
        print(f"  解散日 P576あり: {has_dis}/{n} ({has_dis/n:.1%})")

        samples = [
            (t, dates[q]["inception"], dates[q]["dissolved"])
            for t, q in list(qmap.items())
            if dates.get(q, {}).get("inception")
        ][:5]
        for t, inc, dis in samples:
            print(f"    - {t}: {inc} -> {dis}")


if __name__ == "__main__":
    main()
