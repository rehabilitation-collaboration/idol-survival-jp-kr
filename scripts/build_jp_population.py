"""日本側の母集団を確定させる (Phase 1)。

fetch_jp_population.py が保存した生データに判定ルールを適用し、
母集団 parquet・境界事例リスト・年次分布を出力する。

    .venv/bin/python scripts/build_jp_population.py

出力:
    data/jp_groups.parquet        母集団 (判定陽性のみ)
    results/borderline_cases.md   境界事例 (C1 と C2 が食い違う記事)
    results/population_summary.txt 判定内訳・年次分布・不一致率
"""
import json
import os
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from idol_classifier import classify  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES_PATH = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
INDEX_PATH = os.path.join(ROOT, "data", "raw", "ja_category_index.json")
OUT_PARQUET = os.path.join(ROOT, "data", "jp_groups.parquet")
OUT_BORDERLINE = os.path.join(ROOT, "results", "borderline_cases.md")
OUT_SUMMARY = os.path.join(ROOT, "results", "population_summary.txt")

YEARS = list(range(1996, 2026))


def load_pages():
    rows, broken = [], 0
    with open(PAGES_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                # 取得を中断すると最終行が途中で切れることがある
                broken += 1
                continue
            if rec.get("missing"):
                continue
            rows.append(rec)
    if broken:
        print(f"警告: 破損行 {broken} 件をスキップ")
    return rows


def build():
    pages = load_pages()
    print(f"生データ {len(pages)} 件")

    records = []
    for p in pages:
        r = classify(p.get("categories", []), p.get("lead", ""))
        r["group_id"] = p["title"]
        r["name"] = p["title"]
        r["country"] = "JP"
        r["source_lang"] = "ja"
        r["idol_signal"] = "+".join(
            k for k, v in [("C1", r["c1_category"]), ("C2", r["c2_lead_idol"]), ("C3", r["c3_dance_vocal"])] if v
        ) or "none"
        records.append(r)

    df = pd.DataFrame(records)
    pop = df[df["is_idol"]].copy()

    # 観測窓は 1996-2025。カテゴリ由来の結成年が窓外のものは母集団から外す
    in_window = pop["formed_year_cat"].between(YEARS[0], YEARS[-1])
    out_of_window = int((~in_window).sum())
    pop = pop[in_window].copy()
    pop["formed_year"] = pop["formed_year_cat"].astype(int)
    pop["dissolved_year"] = pop["dissolved_year_cat"]
    pop["is_censored"] = pop["dissolved_year"].isna()

    cols = [
        "group_id", "name", "country", "source_lang", "sex",
        "formed_year", "dissolved_year", "is_censored",
        "c1_category", "c2_lead_idol", "c3_dance_vocal",
        "is_idol", "is_idol_strict", "is_seiyu", "signal_disagree",
        "idol_signal", "lead_sentence",
    ]
    pop[cols].to_parquet(OUT_PARQUET, index=False)

    write_summary(df, pop, out_of_window)
    write_borderline(pop)
    print(f"\n母集団 {len(pop)} 件 -> {OUT_PARQUET}")


def write_summary(df, pop, out_of_window):
    n = len(df)
    lines = []
    a = lines.append
    a("=== 日本母集団 構築サマリ (Phase 1) ===\n")
    a(f"生データ (結成/解散カテゴリの和集合): {n} 件")
    a("")
    a("--- 判定シグナル別の陽性数 (母集団確定前・全生データに対して) ---")
    for key, label in [
        ("c1_category", "C1 アイドル系カテゴリ"),
        ("c2_lead_idol", "C2 冒頭定義文に「アイドル」"),
        ("c3_dance_vocal", "C3 冒頭定義文にダンス&ボーカル"),
        ("is_korean", "除外: 韓国グループ"),
        ("is_seiyu", "参考: 声優ユニット"),
    ]:
        c = int(df[key].sum())
        a(f"  {label:<32} {c:>5} ({c/n:.1%})")
    a("")
    a(f"  ルール D 陽性 (C1 or C2 or C3、韓国除外) {int(df['is_idol'].sum()):>5}")
    a(f"  ルール C 陽性 (C1 or C2、韓国除外)       {int(df['is_idol_strict'].sum()):>5}")
    a(f"  ※ D にのみ含まれる (ダンス&ボーカル系)   {int((df['is_idol'] & ~df['is_idol_strict']).sum()):>5}")
    a("")
    a(f"観測窓 1996-2025 外・結成年不明で除外: {out_of_window} 件")
    a(f"最終母集団: {len(pop)} 件")
    a("")

    a("--- 判定不一致率 (PLAN の分岐条件・20% 超で発動) ---")
    dis = int(pop["signal_disagree"].sum())
    a(f"  C1 XOR C2 の件数 / 母集団 = {dis}/{len(pop)} = {dis/max(len(pop),1):.1%}")
    a(f"  判定: {'★分岐条件 発動 (20% 超)' if dis/max(len(pop),1) > 0.20 else '20% 以下・ルール D を維持'}")
    a("")

    a("--- 判定シグナルの組み合わせ内訳 ---")
    for sig, c in Counter(pop["idol_signal"]).most_common():
        a(f"  {sig:<12} {c:>5}")
    a("")

    a("--- 性別内訳 ---")
    for s, c in Counter(pop["sex"]).most_common():
        a(f"  {s:<10} {c:>5}")
    a("")

    a("--- 年次分布 (結成年・直近年の記事化ラグ判定用) ---")
    a(f"{'年':<8}{'結成':>7}{'うち解散':>9}{'打ち切り':>9}")
    for y in YEARS:
        sub = pop[pop["formed_year"] == y]
        d = int((~sub["is_censored"]).sum())
        a(f"{y:<8}{len(sub):>7}{d:>9}{len(sub)-d:>9}")
    a("-" * 33)
    a(f"{'計':<8}{len(pop):>7}{int((~pop['is_censored']).sum()):>9}{int(pop['is_censored'].sum()):>9}")

    text = "\n".join(lines)
    os.makedirs(os.path.dirname(OUT_SUMMARY), exist_ok=True)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


def write_borderline(pop):
    """C1 と C2 が食い違う記事を全件出す。判定の再現性を担保する Supplement 用。"""
    bl = pop[pop["signal_disagree"]].sort_values(["c1_category", "formed_year"])
    lines = [
        "# 境界事例リスト (アイドル判定の C1/C2 不一致)",
        "",
        "カテゴリ判定 (C1) と冒頭定義文判定 (C2) が食い違った記事の全件。",
        "判定ルールの再現性を担保するため、恣意的な取捨をせず機械的に列挙する。",
        "生成: `.venv/bin/python scripts/build_jp_population.py`",
        "",
        f"件数: {len(bl)} / 母集団 {len(pop)} ({len(bl)/max(len(pop),1):.1%})",
        "",
        "## C1 のみ陽性 (カテゴリはアイドル・冒頭定義文に「アイドル」なし)",
        "",
        "| グループ | 結成年 | 冒頭定義文 |",
        "|---|---|---|",
    ]
    for _, r in bl[bl["c1_category"]].iterrows():
        s = r["lead_sentence"].replace("|", "\\|")[:100]
        lines.append(f"| {r['name']} | {r['formed_year']} | {s} |")

    lines += [
        "",
        "## C2 のみ陽性 (冒頭定義文はアイドル・カテゴリに未収載)",
        "",
        "| グループ | 結成年 | 冒頭定義文 |",
        "|---|---|---|",
    ]
    for _, r in bl[~bl["c1_category"]].iterrows():
        s = r["lead_sentence"].replace("|", "\\|")[:100]
        lines.append(f"| {r['name']} | {r['formed_year']} | {s} |")

    with open(OUT_BORDERLINE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"境界事例 {len(bl)} 件 -> {OUT_BORDERLINE}")


if __name__ == "__main__":
    build()
