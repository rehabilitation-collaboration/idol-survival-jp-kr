"""記事化バイアスの向きを Wikipedia 内部のデータで検証する (Phase 4)。

日本側には韓国の Kim (2026) に相当する産業全数の外部基準が無く、
カバー率を直接は測れない。そこで**向き**だけでも確定させる。

論理:
    1. 記事の充実度 (wikitext のバイト数) は、そのグループの知名度の代理になる
    2. 充実度が低いグループほど短命なら、「記事すら無いグループ」は
       さらに短命である可能性が高い
    3. その場合 Wikipedia ベースの推定は**生存率を過大推定**していることになる

RIAJ 認定の有無でも同じことを確かめる (認定は商業的成功の外部基準)。

    .venv/bin/python scripts/probe_coverage_bias.py
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
SURV = os.path.join(ROOT, "data", "jp_survival.parquet")
CERT = os.path.join(ROOT, "data", "jp_certifications.parquet")
OUT = os.path.join(ROOT, "results", "coverage_bias.md")

CENSOR_YEAR = 2026


def km_survival(durations, observed, t):
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


def load_article_size():
    size = {}
    with open(PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] in size:
                continue
            size[rec["title"]] = len(rec.get("wikitext", "") or "")
    return size


def main():
    surv = pd.read_parquet(SURV)
    cert = pd.read_parquet(CERT)[["group_id", "has_certification"]]
    df = surv.merge(cert, on="group_id", how="left")
    df["article_bytes"] = df["group_id"].map(load_article_size())
    df = df[df["article_bytes"].notna()].copy()

    df["size_quartile"] = pd.qcut(
        df["article_bytes"], 4, labels=["Q1 (最小)", "Q2", "Q3", "Q4 (最大)"]
    )

    lines = []
    a = lines.append
    a("# 記事化バイアスの向きの検証 (Phase 4)")
    a("")
    a("日本側には韓国の Kim (2026) に相当する産業全数の外部基準が存在しない。")
    a("カバー率そのものは測れないので、**バイアスの向き**を内部データで確かめる。")
    a("")
    a("生成: `.venv/bin/python scripts/probe_coverage_bias.py`")
    a("")
    a("## 仮説")
    a("")
    a("記事の充実度 (wikitext のバイト数) はそのグループの知名度の代理になる。")
    a("**充実度が低いグループほど短命**なら、記事すら作られていないグループは")
    a("さらに短命である可能性が高く、Wikipedia ベースの推定は")
    a("**生存率を過大推定している (= 離脱率を過小推定している)** ことになる。")
    a("")

    a("## 記事の充実度と生存 (厳格定義)")
    a("")
    a("| 四分位 | n | 記事バイト数<br>中央値 | 死亡率 | 3 年離脱率 | 7 年離脱率 |")
    a("|---|---|---|---|---|---|")
    for q in df["size_quartile"].cat.categories:
        sub = df[df["size_quartile"] == q]
        e3 = 1 - km_survival(sub["duration_strict"], sub["observed_strict"], 3)
        e7 = 1 - km_survival(sub["duration_strict"], sub["observed_strict"], 7)
        a(f"| {q} | {len(sub)} | {int(sub['article_bytes'].median()):,} | "
          f"{sub['death_strict'].mean():.1%} | {e3:.1%} | {e7:.1%} |")
    a("")

    q1 = df[df["size_quartile"] == "Q1 (最小)"]
    q4 = df[df["size_quartile"] == "Q4 (最大)"]
    e3_q1 = 1 - km_survival(q1["duration_strict"], q1["observed_strict"], 3)
    e3_q4 = 1 - km_survival(q4["duration_strict"], q4["observed_strict"], 3)
    a(f"**最小四分位と最大四分位の 3 年離脱率の差: {(e3_q1 - e3_q4) * 100:+.1f} pt**")
    a("")

    a("## 商業的成功 (RIAJ 認定) と生存")
    a("")
    a("| 区分 | n | 死亡率 | 3 年離脱率 | 7 年離脱率 |")
    a("|---|---|---|---|---|")
    for flag, label in [(True, "認定あり"), (False, "認定なし")]:
        sub = df[df["has_certification"] == flag]
        e3 = 1 - km_survival(sub["duration_strict"], sub["observed_strict"], 3)
        e7 = 1 - km_survival(sub["duration_strict"], sub["observed_strict"], 7)
        a(f"| {label} | {len(sub)} | {sub['death_strict'].mean():.1%} | {e3:.1%} | {e7:.1%} |")
    a("")

    cert_yes = df[df["has_certification"] == True]  # noqa: E712
    cert_no = df[df["has_certification"] == False]  # noqa: E712
    e3_yes = 1 - km_survival(cert_yes["duration_strict"], cert_yes["observed_strict"], 3)
    e3_no = 1 - km_survival(cert_no["duration_strict"], cert_no["observed_strict"], 3)

    a("## 判定")
    a("")
    same_direction = (e3_q1 > e3_q4) and (e3_no > e3_yes)
    if same_direction:
        a("**2 つの代理指標が同じ向きを示した。**")
        a("")
        a(f"- 記事が薄いグループほど 3 年離脱率が高い ({e3_q1:.1%} vs {e3_q4:.1%})")
        a(f"- 商業的成功が無いグループほど 3 年離脱率が高い ({e3_no:.1%} vs {e3_yes:.1%})")
        a("")
        a("→ **知名度が低いグループほど短命**。記事が作られていないグループは")
        a("さらに知名度が低いはずなので、Wikipedia ベースの母集団は")
        a("**短命なグループを系統的に取りこぼしており、離脱率を過小推定している**。")
        a("")
        a("これは韓国側で観測された乖離 (Kim 2026 の 45% に対し本研究 20.1%) と")
        a("**同じ向き**であり、乖離の主因が記事化バイアスであるという解釈と整合する。")
    else:
        a("**2 つの代理指標が同じ向きを示さなかった。** 記事化バイアスの向きは確定できない。")
        a(f"- 記事の薄さ: {e3_q1:.1%} vs {e3_q4:.1%}")
        a(f"- 認定の有無: {e3_no:.1%} vs {e3_yes:.1%}")
    a("")

    a("## この検証の限界")
    a("")
    a("- 記事の充実度は知名度の**代理**にすぎない。長期活動するほど記事が育つため、")
    a("  「充実度が高い→長命」には**逆の因果 (長命だから記事が育つ) が含まれる**")
    a("- したがってこの結果は**バイアスの向きの傍証**であって、")
    a("  カバー率そのものの推定ではない")
    a("- 日本側のカバー率は依然として不明。**Limitations の主要項目として明記する**")
    a("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
