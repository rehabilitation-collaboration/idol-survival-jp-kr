"""PLAN「一次確認済みデータ」節のカテゴリ件数を全て再現する。

このスクリプトが出力する数値が、プロジェクト全体の実現可能性の根拠。
PLAN / handoff の数値を疑ったとき、または最新化したいときはこれを実行する。

    python3 scripts/probe_categories.py

2026-08-07 実測時の期待値 (Wikipedia は日々更新されるので完全一致はしない):
    ja 結成年カテゴリ 1996-2025 合計 = 6,620
    ja 解散年カテゴリ 1996-2025 合計 = 2,484
    ja 日本の女性アイドルグループ     = 1,696
    ja 日本の男性アイドルグループ     =   140
    ko 대한민국의 아이돌 그룹         =   414
    ko 年別カテゴリ                   = 存在しない (missing)
    en K-pop music groups             =   571
    en Japanese idol groups           =   312
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "IdolSurvivalResearch/0.1 (category census)"
YEARS = list(range(1996, 2026))
BATCH = 40  # titles= に | 区切りで渡せる上限に対する安全値。429 回避の要


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


def category_sizes(lang, categories):
    """カテゴリ名 -> 所属ページ数。存在しないカテゴリは -1 を返す。

    1 件ずつ叩くと 429 になるので titles= にまとめて投げる。
    """
    out = {}
    for i in range(0, len(categories), BATCH):
        chunk = categories[i : i + BATCH]
        q = urllib.parse.quote("|".join(f"Category:{c}" for c in chunk))
        d = api_get(
            f"https://{lang}.wikipedia.org/w/api.php?action=query&titles={q}"
            f"&prop=categoryinfo&format=json"
        )
        for p in d["query"]["pages"].values():
            # 名前空間プレフィックスは言語ごとに違う (ja/en は "Category:"、ko は "분류:")。
            # "Category:" 決め打ちで剥がすと ko だけキーが一致せず全件 missing に見える。
            name = p["title"].split(":", 1)[-1]
            out[name] = -1 if "missing" in p else (p.get("categoryinfo") or {}).get("pages", 0)
        time.sleep(2)
    return out


def report_year_categories(lang, formed_tpl, dissolved_tpl, label):
    formed = [formed_tpl.format(y=y) for y in YEARS]
    dissolved = [dissolved_tpl.format(y=y) for y in YEARS]
    sizes = category_sizes(lang, formed + dissolved)

    print(f"\n=== {label} ({lang}.wikipedia) ===")
    print(f"{'年':<6}{'結成':>8}{'解散':>8}")
    tf = td = 0
    missing = 0
    for y in YEARS:
        f = sizes.get(formed_tpl.format(y=y), -1)
        d = sizes.get(dissolved_tpl.format(y=y), -1)
        if f < 0 or d < 0:
            missing += 1
        tf += max(f, 0)
        td += max(d, 0)
        print(f"{y:<6}{f:>8}{d:>8}")
    print("-" * 22)
    print(f"{'計':<6}{tf:>8}{td:>8}")
    if missing:
        print(f"  ※ {missing}/{len(YEARS)} 年で片方以上のカテゴリが存在しない (-1)")
    return tf, td


def main():
    # --- 日本: 年別カテゴリ (母集団の主軸) ---
    jp_formed, jp_dissolved = report_year_categories(
        "ja", "{y}年に結成した音楽グループ", "{y}年に解散した音楽グループ", "日本 年別カテゴリ"
    )

    # --- 韓国: 年別カテゴリが存在しないことの確認 ---
    report_year_categories(
        "ko", "{y}년에 결성한 음악 그룹", "{y}년에 해체한 음악 그룹", "韓国 年別カテゴリ (存在しない想定)"
    )

    # --- 各国語版・英語版のアイドル/音楽グループカテゴリ ---
    print("\n=== 各言語版 アイドル/音楽グループ カテゴリ ===")
    for lang, cats in [
        ("ja", ["日本の女性アイドルグループ", "日本の男性アイドルグループ", "日本のアイドルグループ"]),
        ("ko", ["대한민국의 아이돌 그룹", "대한민국의 음악 그룹"]),
        (
            "en",
            [
                "K-pop music groups",
                "South Korean boy bands",
                "South Korean girl groups",
                "South Korean idol groups",
                "Japanese idol groups",
                "Japanese girl groups",
                "Japanese boy bands",
            ],
        ),
    ]:
        sizes = category_sizes(lang, cats)
        print(f"  [{lang}]")
        for c in cats:
            v = sizes.get(c, -1)
            print(f"    {c}: {'存在しない' if v < 0 else v}")

    # --- 英語版の年別カテゴリ (日韓対称化に使う・全世界対象なので国別との交差が必要) ---
    print("\n=== en 年別カテゴリ (全世界対象・サンプル年のみ) ===")
    sample = [1996, 2010, 2020, 2025]
    cats = [f"Musical groups established in {y}" for y in sample] + [
        f"Musical groups disestablished in {y}" for y in sample
    ]
    sizes = category_sizes("en", cats)
    for y in sample:
        e = sizes.get(f"Musical groups established in {y}", -1)
        d = sizes.get(f"Musical groups disestablished in {y}", -1)
        print(f"  {y}: established={e}  disestablished={d}")

    print("\n--- サマリ (PLAN の一次確認済みデータ節と照合すること) ---")
    print(f"  ja 結成年カテゴリ 1996-2025 合計 = {jp_formed}")
    print(f"  ja 解散年カテゴリ 1996-2025 合計 = {jp_dissolved}")


if __name__ == "__main__":
    main()
