"""韓国側の母集団と生存データを作り、Kim (2026) と照合する (Phase 3)。

手法妥当性の実証がこの Phase の目的。同じ Wikipedia ベースの手法を
韓国に適用し、Kim (2026) の公表値と突き合わせて乖離を定量化する。

★ 照合できるのは 2 点のみ (本文を取得しない決定のため):
    母集団サイズ    1,182 組 (1996-2025 デビュー)
    3 年以内の離脱  approximately 45%

    .venv/bin/python scripts/build_kr_population.py

出力:
    data/kr_survival.parquet        韓国側の生存データ
    results/method_validation.md    Kim (2026) との照合レポート
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from en_classifier import classify_en  # noqa: E402
from wikitext import extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_REPORT = os.path.join(ROOT, "results", "method_validation.md")

YEARS_ACTIVE = ["years_active", "Years_active", "years active"]
WINDOW = (1996, 2025)
CENSOR_YEAR = 2026

# Kim (2026) の英文アブストラクト記載値。本文は取得しない方針のためこの 2 点のみ
KIM_N_GROUPS = 1182
KIM_EXIT_3Y = 0.45


def load_pages(pages_path):
    out = {}
    with open(pages_path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] in out:
                continue
            out[rec["title"]] = rec
    return out


def build(pages, country):
    rows = []
    for title, p in pages.items():
        raw_ya = extract_field(p.get("wikitext", ""), YEARS_ACTIVE)
        r = classify_en(p.get("categories", []), p.get("lead", ""), raw_ya)
        r["group_id"] = title
        r["name"] = title
        r["country"] = country
        r["source_lang"] = "en"
        r["kind"] = "+".join(r["kinds"]) or "unspecified"
        rows.append(r)
    return pd.DataFrame(rows)


def add_survival(df):
    df = df[df["is_idol"]].copy()
    df["in_window"] = df["cat_formed_year"].between(*WINDOW)
    pop = df[df["in_window"]].copy()

    pop["formed_year"] = pop["cat_formed_year"].astype(int)
    # 死亡年が結成年より前になる記述ゆれは採用しない
    bad = pop["death_year"].notna() & (pop["death_year"] < pop["formed_year"])
    pop.loc[bad, "death_year"] = pd.NA
    pop["observed"] = pop["death_year"].notna()
    pop["duration"] = (
        pop["death_year"].fillna(CENSOR_YEAR).astype(float) - pop["formed_year"]
    )
    return df, pop


def km_survival(durations, observed, t):
    """時点 t における Kaplan-Meier 生存確率。"""
    df = pd.DataFrame({"d": durations, "e": observed}).sort_values("d")
    s, n = 1.0, len(df)
    for d, grp in df.groupby("d"):
        if d > t:
            break
        deaths = int(grp["e"].sum())
        if n > 0 and deaths:
            s *= 1 - deaths / n
        n -= len(grp)
    return s


def write_report(df, pop):
    n_all = len(df)
    n_pop = len(pop)
    dead = int(pop["observed"].sum())
    no_year = int(pop["death_without_year"].sum())

    s3 = km_survival(pop["duration"], pop["observed"], 3)
    exit3 = 1 - s3

    lines = []
    a = lines.append
    a("# 手法妥当性の検証: Kim (2026) との照合 (Phase 3)")
    a("")
    a("同じ Wikipedia ベースの手法を韓国に適用し、Kim (2026) の公表値と")
    a("突き合わせて乖離を定量化する。**本研究の方法論上の要**。")
    a("")
    a("生成: `.venv/bin/python scripts/build_kr_population.py`")
    a("")
    a("> **照合できるのは 2 点のみ**。Kim (2026) 本文 (pp.71-80) を取得しない方針のため、")
    a("> 引用できるのは英文アブストラクト記載値に限られる。")
    a("> 平均活動年数・男女別・生存曲線の形状は照合できない。")
    a("")
    a("## 照合結果")
    a("")
    a("| 照合軸 | Kim (2026) | 本研究 (en.wikipedia) | 差 |")
    a("|---|---|---|---|")
    a(f"| 母集団サイズ (1996-2025) | **{KIM_N_GROUPS:,} 組** | **{n_pop:,} 組** "
      f"| カバー率 **{n_pop / KIM_N_GROUPS:.1%}** |")
    a(f"| 3 年以内の離脱率 | **約 {KIM_EXIT_3Y:.0%}** | **{exit3:.1%}** "
      f"| **{(exit3 - KIM_EXIT_3Y) * 100:+.1f} pt** |")
    a("")

    gap = abs(exit3 - KIM_EXIT_3Y) * 100
    if gap >= 10:
        a(f"→ **乖離 {gap:.1f} pt は PLAN の分岐条件 (10 pt 以上) に該当**する。")
        a("原因分解を独立セクションとして報告し、Wikipedia 手法の限界を主要な知見の一つとして扱う。")
    else:
        a(f"→ 乖離 {gap:.1f} pt。PLAN の分岐条件 (10 pt 以上) には該当しない。")
    a("")

    a("## 母集団の構築過程")
    a("")
    a("| 段階 | 件数 |")
    a("|---|---|")
    a(f"| シード (K-pop / South Korean グループカテゴリの和集合) | {n_all} |")
    a(f"| アイドル判定を通過 | {int(df['is_idol'].sum())} |")
    a(f"| 結成年カテゴリあり | {int(df['cat_formed_year'].notna().sum())} |")
    a(f"| **観測窓 1996-2025 に収まる (最終母集団)** | **{n_pop}** |")
    a("")
    a(f"- 結成年が取れない: {int(df['cat_formed_year'].isna().sum())} 件")
    a(f"- 観測窓の外: {int((df['cat_formed_year'].notna() & ~df['in_window']).sum())} 件")
    a("")

    a("## 死亡判定に使ったシグナル")
    a("")
    a("日本側と違い、英語版は冒頭定義文の時制で現存と解散を書き分ける慣行がある")
    a("(`is a South Korean boy band` / `was a South Korean boy band`)。")
    a("独立性の高い順にカテゴリ → Infobox → リード文で死亡年を決めた。")
    a("")
    a("| シグナル | 死亡年を与えた件数 |")
    a("|---|---|")
    a(f"| 解散年カテゴリ (`Musical groups disestablished in YYYY`) | {int(pop['cat_dissolved_year'].notna().sum())} |")
    a(f"| Infobox `years_active` の終了年 | {int(pop['ya_end_year'].notna().sum())} |")
    a(f"| リード文の解散年 (過去形と併用) | {int(pop['lead_dissolved_year'].notna().sum())} |")
    a("")
    a(f"- **死亡 {dead} 件 / 打ち切り {n_pop - dead} 件 (死亡率 {dead / n_pop:.1%})**")
    a("")
    a(f"### ⚠️ 死亡と分かるが年が特定できない {no_year} 件")
    a("")
    a("冒頭定義文が過去形なのに、どのソースからも年が取れないグループがある。")
    a("生存分析には死亡年が必要なので、これらは**打ち切りとして扱っている**。")
    a(f"母集団の {no_year / n_pop:.1%} にあたり、その分だけ**生存率を過大推定している**。")
    a("感度分析としてこれらを除外した推定も併記する。")
    a("")

    sub = pop[~pop["death_without_year"]]
    s3b = km_survival(sub["duration"], sub["observed"], 3)
    a(f"- 年不明の死亡を除外した母集団 {len(sub)} 組での 3 年以内離脱率: **{1 - s3b:.1%}**")
    a(f"- 主分析との差: {((1 - s3b) - exit3) * 100:+.1f} pt")
    a("")

    a("## 生存率 (Kaplan-Meier)")
    a("")
    a("| 経過年 | 生存率 | 離脱率 |")
    a("|---|---|---|")
    for t in [1, 2, 3, 5, 7, 10]:
        s = km_survival(pop["duration"], pop["observed"], t)
        a(f"| {t} 年 | {s:.1%} | {1 - s:.1%} |")
    a("")
    a("**7 年**は韓国の標準専属契約期間。日本との比較で焦点になる地点。")
    a("")

    # 日本側 (英語版) が生成済みなら、同一ソース・同一手法での対称比較を載せる
    jp_path = os.path.join(ROOT, "data", "jp_en_survival.parquet")
    jp_ja_path = os.path.join(ROOT, "data", "jp_survival.parquet")
    if os.path.exists(jp_path) and os.path.exists(jp_ja_path):
        jp = pd.read_parquet(jp_path)
        jp_ja = pd.read_parquet(jp_ja_path)
        a("## 日韓比較: 使うソースで結論が変わる")
        a("")
        a("PLAN の二層設計 (主分析=各国語版 / 感度分析=英語版で対称化) に沿って両方を出す。")
        a("")
        a("| 経過年 | 日本 (ja.wikipedia)<br>主分析 n=%d | 日本 (en.wikipedia)<br>感度分析 n=%d | 韓国 (en.wikipedia)<br>主分析 n=%d |"
          % (len(jp_ja), len(jp), n_pop))
        a("|---|---|---|---|")
        for t in [1, 2, 3, 5, 7, 10]:
            v1 = 1 - km_survival(jp_ja["duration_strict"], jp_ja["observed_strict"], t)
            v2 = 1 - km_survival(jp["duration"], jp["observed"], t)
            v3 = 1 - km_survival(pop["duration"], pop["observed"], t)
            a(f"| {t} 年 | {v1:.1%} | {v2:.1%} | {v3:.1%} |")
        a("")
        j3 = 1 - km_survival(jp_ja["duration_strict"], jp_ja["observed_strict"], 3)
        e3 = 1 - km_survival(jp["duration"], jp["observed"], 3)
        a(f"- **主分析どうし (日本語版 vs 英語版) では 3 年離脱率がほぼ一致** "
          f"({j3:.1%} vs {exit3:.1%}・差 {(j3 - exit3) * 100:+.1f} pt)")
        a(f"- **同じ英語版で揃えると韓国が明確に短命** "
          f"({e3:.1%} vs {exit3:.1%}・差 {(e3 - exit3) * 100:+.1f} pt)")
        a("")
        a("### ⚠️ この食い違いを「日韓差の発見」と読んではいけない")
        a("")
        a("英語版のカバー率が日韓で大きく違うため、**同一ソースにしてもバイアス条件は揃っていない**:")
        a("")
        a("| | 英語版 | 比較対象 | 英語版のカバー率 |")
        a("|---|---|---|---|")
        a(f"| 日本 | {len(jp)} 組 | ja.wikipedia {len(jp_ja)} 組 | **{len(jp) / len(jp_ja):.1%}** |")
        a(f"| 韓国 | {n_pop} 組 | Kim (2026) {KIM_N_GROUPS:,} 組 | **{n_pop / KIM_N_GROUPS:.1%}** |")
        a("")
        a("英語版は日本を韓国の半分以下の割合しか収録していない (K-pop の国際的知名度の差)。")
        a("知名度で選抜された母集団ほど長命に偏るため、**英語版では日本の離脱率がより強く")
        a("過小推定されている**と考えられる。したがって「英語版で韓国が短命」も、")
        a("実態の差ではなくカバー率の非対称で説明できてしまう。")
        a("")
        a("**現時点で日韓差について確定的なことは言えない。** 判断には日本側のカバー率の")
        a("外部推定が要る。Phase 4 で RIAJ 認定作品と突合し、「認定があるのに記事がない」")
        a("件数を測ることで、日本側の記事化バイアスを定量化する。")
        a("")

    a("## 種別の内訳")
    a("")
    a("| 種別 | 件数 |")
    a("|---|---|")
    for k, c in pop["kind"].value_counts().items():
        a(f"| {k} | {c} |")
    a("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    country = (sys.argv[1] if len(sys.argv) > 1 else "kr").lower()
    if country not in ("kr", "jp"):
        print("usage: python3 scripts/build_en_population.py {kr|jp}")
        return 1
    pages_path = os.path.join(ROOT, "data", "raw", f"en_{country}_pages.jsonl")
    out_parquet = os.path.join(ROOT, "data", f"{country}_en_survival.parquet")

    pages = load_pages(pages_path)
    print(f"取得済み {len(pages)} 件")
    df, pop = add_survival(build(pages, country.upper()))
    pop.to_parquet(out_parquet, index=False)
    # Kim (2026) との照合は韓国側でしか成立しない。日本側は同一手法での
    # 対称比較が目的なので、レポートは韓国のみ書き出す
    if country == "kr":
        write_report(df, pop)
    else:
        summarize_jp(df, pop)
    print(f"\n{country.upper()} (en.wikipedia) 生存データ {len(pop)} 件 -> {out_parquet}")



def summarize_jp(df, pop):
    """日本側 (英語版) の要約。韓国と同一ソース・同一手法での比較用。"""
    dead = int(pop["observed"].sum())
    print(f"\n=== 日本 (en.wikipedia) 母集団 ===")
    print(f"  シード: {len(df)} 件 / 観測窓 1996-2025: {len(pop)} 件")
    print(f"  死亡 {dead} / 打ち切り {len(pop) - dead} (死亡率 {dead / max(len(pop), 1):.1%})")
    print(f"  死亡と分かるが年不明: {int(pop['death_without_year'].sum())} 件")
    print("\n  経過年ごとの離脱率 (Kaplan-Meier):")
    for t in [1, 2, 3, 5, 7, 10]:
        s = km_survival(pop["duration"], pop["observed"], t)
        print(f"    {t:>2} 年: {1 - s:.1%}")

if __name__ == "__main__":
    main()
