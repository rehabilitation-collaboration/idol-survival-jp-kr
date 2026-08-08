"""日本側の生存データを作る (Phase 2)。

母集団の各グループについて、結成と解散を 2 つの独立したソースから取り、
食い違いを測ってから死亡定義 3 種を組み立てる。

    ソース A: 年別カテゴリ (YYYY年に結成/解散した音楽グループ)
    ソース B: Infobox「活動期間」

    .venv/bin/python scripts/build_jp_survival.py

出力:
    data/jp_survival.parquet      生存データ
    results/source_agreement.md   二重ソース照合レポート
"""
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wikitext import extract_field  # noqa: E402
from years_active import detect_lead_end, parse_years_active  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
POP = os.path.join(ROOT, "data", "jp_groups.parquet")
OUT_PARQUET = os.path.join(ROOT, "data", "jp_survival.parquet")
OUT_REPORT = os.path.join(ROOT, "results", "source_agreement.md")

YEARS_ACTIVE = ["活動期間", "活動年数", "Years_active", "years_active", "Years active"]

# 打ち切り時点。母集団を取得した日で全グループを行政的に打ち切る
CENSOR_YEAR = 2026

# リード文で休止・終了が示唆される場合に、その年を拾う。
# 「2020年に活動休止」「2020年より活動休止」のように年が直前に来る形だけを採り、
# 離れた位置の年は拾わない (誤検出を避ける)
LEAD_END_YEAR = re.compile(
    r"(\d{4})\s*年(?:[^。]{0,12}?)(?:をもって|より|から|に)?[^。]{0,12}?"
    r"(?:活動休止|活動を休止|活動停止|活動終了|活動を終了|解散)"
)


def load_pages(pop_ids):
    out = {}
    with open(PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] not in pop_ids or rec["title"] in out:
                continue
            out[rec["title"]] = rec
    return out


def build_rows(pop, pages):
    rows = []
    for _, g in pop.iterrows():
        rec = pages.get(g["group_id"], {})
        raw = extract_field(rec.get("wikitext", ""), YEARS_ACTIVE)
        ya = parse_years_active(raw)
        lead = rec.get("lead", "")
        lead_end = detect_lead_end(lead)
        m = LEAD_END_YEAR.search(lead or "")
        lead_end_year = int(m.group(1)) if m else None

        cat_formed = int(g["formed_year"])
        cat_dissolved = None if pd.isna(g["dissolved_year"]) else int(g["dissolved_year"])

        rows.append({
            "group_id": g["group_id"],
            "name": g["name"],
            "sex": g["sex"],
            "is_idol_strict_pop": bool(g["is_idol_strict"]),
            "definition_sensitive": bool(g["definition_sensitive"]),
            # --- ソース A: 年別カテゴリ ---
            "cat_formed_year": cat_formed,
            "cat_dissolved_year": cat_dissolved,
            # --- ソース B: Infobox 活動期間 ---
            "ib_start_year": ya["start_year"],
            "ib_end_year": ya["end_year"],
            "ib_ongoing": ya["is_ongoing"],
            "ib_end_reason": ya["end_reason"],
            "has_years_active": raw is not None,
            # --- リード文 ---
            "lead_end_reason": lead_end,
            "lead_end_year": lead_end_year,
        })
    return pd.DataFrame(rows)


def add_definitions(df):
    """死亡定義 3 種と生存時間を付ける。"""
    # 保守: 解散年カテゴリのみを死亡とする
    df["death_conservative"] = df["cat_dissolved_year"].notna()
    df["year_conservative"] = df["cat_dissolved_year"]

    # 厳格 (主分析): 解散年カテゴリ or Infobox の終了年
    df["death_strict"] = df["cat_dissolved_year"].notna() | df["ib_end_year"].notna()
    df["year_strict"] = df["cat_dissolved_year"].fillna(df["ib_end_year"])

    # 緩和: 厳格 + リード文で休止・終了が示唆され、かつその年が特定できるもの。
    # 年が取れないものは死亡年を置けないので打ち切りのままにする
    hiatus = df["lead_end_reason"].isin(["hiatus", "indefinite_hiatus", "ended"])
    add = hiatus & ~df["death_strict"] & df["lead_end_year"].notna()
    df["death_loose"] = df["death_strict"] | add
    df["year_loose"] = df["year_strict"].where(~add, df["lead_end_year"])
    df["loose_only"] = add

    for name in ["conservative", "strict", "loose"]:
        y = df[f"year_{name}"]
        dead = df[f"death_{name}"]
        # 解散年が結成年より前になる記述ゆれは死亡年を採用せず打ち切る
        invalid = dead & y.notna() & (y < df["cat_formed_year"])
        dead = dead & ~invalid
        y = y.where(~invalid)
        df[f"death_{name}"] = dead
        df[f"year_{name}"] = y
        df[f"invalid_{name}"] = invalid
        df[f"duration_{name}"] = (y.fillna(CENSOR_YEAR) - df["cat_formed_year"]).astype(float)
        df[f"observed_{name}"] = dead
    return df


def write_report(df):
    n = len(df)
    lines = []
    a = lines.append
    a("# 二重ソース照合レポート (Phase 2)")
    a("")
    a("結成と解散を 2 つの独立したソースから取り、食い違いを測る。")
    a("")
    a("- **ソース A**: 年別カテゴリ (`YYYY年に結成/解散した音楽グループ`)")
    a("- **ソース B**: Infobox「活動期間」")
    a("")
    a("生成: `.venv/bin/python scripts/build_jp_survival.py`")
    a("")
    a(f"母集団: {n} 件")
    a("")

    a("## Infobox「活動期間」の取得状況")
    a("")
    a(f"- フィールドあり: {int(df['has_years_active'].sum())} 件 ({df['has_years_active'].mean():.1%})")
    a(f"- 開始年を取得: {int(df['ib_start_year'].notna().sum())} 件 ({df['ib_start_year'].notna().mean():.1%})")
    a(f"- 終了年を取得: {int(df['ib_end_year'].notna().sum())} 件 ({df['ib_end_year'].notna().mean():.1%})")
    a(f"- 現役と判定: {int(df['ib_ongoing'].sum())} 件 ({df['ib_ongoing'].mean():.1%})")
    a("")

    a("## 結成年の照合")
    a("")
    both = df[df["ib_start_year"].notna()]
    match = both["cat_formed_year"] == both["ib_start_year"]
    diff = (both["ib_start_year"] - both["cat_formed_year"]).abs()
    a(f"- 両ソースあり: {len(both)} 件")
    a(f"- **一致: {int(match.sum())} 件 ({match.mean():.1%})**")
    a(f"- 1 年差: {int((diff == 1).sum())} 件 / 2 年以上差: {int((diff >= 2).sum())} 件")
    a("")
    a("差が大きい例 (上位 10 件):")
    a("")
    a("| グループ | カテゴリ | Infobox | 差 |")
    a("|---|---|---|---|")
    for _, r in both.assign(d=diff).nlargest(10, "d").iterrows():
        a(f"| {r['name']} | {r['cat_formed_year']} | {int(r['ib_start_year'])} | {int(r['d'])} |")
    a("")

    a("## 解散の照合")
    a("")
    cat = df["cat_dissolved_year"].notna()
    ib = df["ib_end_year"].notna()
    a("| | Infobox 終了年あり | Infobox 終了年なし | 計 |")
    a("|---|---|---|---|")
    a(f"| **解散カテゴリあり** | {int((cat & ib).sum())} | {int((cat & ~ib).sum())} | {int(cat.sum())} |")
    a(f"| **解散カテゴリなし** | {int((~cat & ib).sum())} | {int((~cat & ~ib).sum())} | {int((~cat).sum())} |")
    a(f"| **計** | {int(ib.sum())} | {int((~ib).sum())} | {n} |")
    a("")
    agree = df[cat & ib]
    same = agree["cat_dissolved_year"] == agree["ib_end_year"]
    a(f"両方にある {len(agree)} 件のうち、**年が一致: {int(same.sum())} 件 ({same.mean():.1%})**")
    a("")
    a(f"- **カテゴリのみが死亡と判定: {int((cat & ~ib).sum())} 件** (Infobox は現役表記のまま更新されていない)")
    a(f"- **Infobox のみが死亡と判定: {int((~cat & ib).sum())} 件** (解散年カテゴリが付与されていない)")
    a("")
    a("→ **どちらか一方だけでは死亡を取りこぼす**。厳格定義で両方を使う根拠。")
    a("")

    a("## 死亡定義 3 種の比較")
    a("")
    a("| 定義 | 内容 | 死亡 | 打ち切り | 死亡率 |")
    a("|---|---|---|---|---|")
    for key, desc in [
        ("conservative", "解散年カテゴリのみ"),
        ("strict", "解散年カテゴリ or Infobox 終了年 (**主分析**)"),
        ("loose", "厳格 + リード文の休止・終了 (年が特定できるもの)"),
    ]:
        d = int(df[f"death_{key}"].sum())
        a(f"| {key} | {desc} | {d} | {n - d} | {d / n:.1%} |")
    a("")
    a(f"- 緩和が厳格に追加する件数: {int(df['loose_only'].sum())} 件")
    a(f"- 解散年 < 結成年で無効とした件数 (厳格): {int(df['invalid_strict'].sum())} 件")
    a("")

    a("## 生存時間の分布 (厳格定義)")
    a("")
    d = df[df["death_strict"]]["duration_strict"]
    a(f"- 死亡 {len(d)} 件の活動年数: 中央値 {d.median():.1f} 年 / 平均 {d.mean():.2f} 年")
    a(f"- 3 年以内に死亡: {int((d <= 3).sum())} 件 (死亡例のうち {(d <= 3).mean():.1%})")
    a("")
    a("※ これは死亡例のみの単純集計であり、打ち切りを含む生存率ではない。")
    a("Kaplan-Meier による推定は Phase 5 で行う。")
    a("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    pop = pd.read_parquet(POP)
    pages = load_pages(set(pop["group_id"]))
    df = add_definitions(build_rows(pop, pages))
    df.to_parquet(OUT_PARQUET, index=False)
    write_report(df)
    print(f"\n生存データ {len(df)} 件 -> {OUT_PARQUET}")


if __name__ == "__main__":
    main()
