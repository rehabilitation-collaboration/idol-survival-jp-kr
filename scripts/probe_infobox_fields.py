"""Infobox にどのフィールドが実在するかを頻度で測る。

Phase 1「アイドル判定レイヤー」の設計根拠を作るためのスクリプト。
判定に使えるフィールド (事務所・レーベル・ジャンル等) が
実際にどれだけ埋まっているかを知らずにルールを設計してはいけない。

    python3 scripts/probe_infobox_fields.py

出力: フィールド名の出現率 (降順) と、判定候補フィールドの実測カバー率。
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

UA = "IdolSurvivalResearch/0.1 (infobox field census)"
SAMPLE_LIMIT = 150

# Infobox のフィールド行。値が複数行に渡るケースは名前だけ拾えればよい。
FIELD = re.compile(r"^\s*\|\s*([A-Za-z0-9_ぁ-んァ-ヶ一-龠]+)\s*=", re.M)

# アイドル判定に使えそうな候補。
# ★日本語版 Wikipedia には {{Infobox Musician}} (日本語フィールド名) と
#   {{Infobox musical artist}} (英語フィールド名) が混在している。
#   片方だけ数えると実力の半分しか見えないので、必ずエイリアスで合算する。
CANDIDATES = {
    "事務所": ["事務所", "Production", "production"],
    "レーベル": ["レーベル", "Label", "label"],
    "ジャンル": ["ジャンル", "Genre", "genre"],
    "活動期間": ["活動期間", "活動年数", "Years_active", "years_active"],
    "出身地": ["出身地", "Origin", "origin"],
    "現メンバー": ["メンバー", "現メンバー", "Current_members", "current_members"],
    "共同作業者": ["共同作業者", "Associated_acts", "associated_acts"],
}


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
        q = urllib.parse.quote("|".join(titles[i : i + 20]))
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


def main():
    for cat in ["日本の女性アイドルグループ", "日本の男性アイドルグループ"]:
        titles = category_members(cat, SAMPLE_LIMIT)
        texts = fetch_wikitext(titles)
        n = len(texts)

        counter = Counter()
        for wt in texts.values():
            # 1 記事内で同じフィールドが複数回出ても 1 回として数える
            counter.update(set(FIELD.findall(wt)))

        print(f"\n=== {cat} (wikitext {n} 件) ===")
        print("--- 出現率 上位 20 フィールド ---")
        for name, c in counter.most_common(20):
            print(f"  {name:<16} {c:>4}/{n}  ({c/n:.1%})")

        print("--- アイドル判定の候補フィールド (日英エイリアス合算) ---")
        for label, aliases in CANDIDATES.items():
            # 同一記事が日英両方を持つことはないので、記事単位で「どれか1つでもあるか」を数える
            c = sum(1 for wt in texts.values() if set(FIELD.findall(wt)) & set(aliases))
            verdict = "使える" if c / n >= 0.6 else ("要注意" if c / n >= 0.3 else "使えない")
            detail = " + ".join(f"{a}:{counter.get(a, 0)}" for a in aliases if counter.get(a, 0))
            print(f"  {label:<10} {c:>4}/{n}  ({c/n:.1%})  -> {verdict}   [{detail}]")


if __name__ == "__main__":
    main()
