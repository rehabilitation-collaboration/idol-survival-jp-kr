"""Phase 5: 生存分析。

    .venv/bin/python scripts/analyze_survival.py

Kaplan-Meier / log-rank / Cox / Schoenfeld に加え、本研究の核心である
**7 年地点のハザード集中**を検証する。韓国の標準専属契約は 7 年で、
制度が生存構造を規定するなら韓国側に t=7 の超過ハザードが出るはず。

出力:
    results/analysis.md          本文用の全結果
    results/hazard_by_year.csv   離散時間ハザードの生値
    plots/*.png                  図 (ラベルは英語のみ・PDF の CJK 問題を避ける)
"""
import os
import sys

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import survival_analysis as sa  # noqa: E402
import report_hazard as rh  # noqa: E402
import report_sections as rs  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_MD = os.path.join(ROOT, "results", "analysis.md")
OUT_HAZARD = os.path.join(ROOT, "results", "hazard_by_year.csv")
PLOTS = os.path.join(ROOT, "plots")

TIMES = [1, 2, 3, 5, 7, 10, 15]

# ハザード図の描画上限。results/analysis.md §4.1 の表と同じ範囲にする
# (図だけ 15 年まで伸ばすと表と食い違って見える)。
HAZARD_PLOT_TMAX = 12


def load_panels():
    """3 つの母集団を同じ列名に揃える。

    主分析は各国で最も網羅的なソース (日本 = ja / 韓国 = en)、
    感度分析は英語版で対称化 (日本 en vs 韓国 en)。PLAN の二層設計。
    """
    jp = pd.read_parquet(os.path.join(ROOT, "data", "jp_survival.parquet"))
    kr = pd.read_parquet(os.path.join(ROOT, "data", "kr_en_survival.parquet"))
    jp_en = pd.read_parquet(os.path.join(ROOT, "data", "jp_en_survival.parquet"))

    panels = {}
    for key, df, dur, ev, country, src in [
        ("jp_ja", jp, "duration_strict", "observed_strict", "JP", "ja"),
        ("kr_en", kr, "duration", "observed", "KR", "en"),
        ("jp_en", jp_en, "duration", "observed", "JP", "en"),
    ]:
        p = pd.DataFrame({
            "group_id": df["group_id"],
            "country": country,
            "source": src,
            "sex": df["sex"],
            "formed_year": df["cat_formed_year"].astype(int)
            if "cat_formed_year" in df else df["formed_year"].astype(int),
            "duration": df[dur].astype(float),
            "event": df[ev].astype(int),
        })
        p["cohort"] = sa.to_cohort(p["formed_year"])
        if src == "en":
            p["sex_cat"] = df["sex_cat"]
            p["sex_lead"] = df["sex_lead"]
        if key == "jp_ja":
            # 事務所規模。無所属は 3 件しかなく水準として成立しないので
            # 「所属グループ 1 組」に畳む (実質的に同じ規模)
            p["agency_class"] = df["agency_class"].replace({"independent": "1"})
            p["agency"] = df["agency"]
            p["definition_sensitive"] = df["definition_sensitive"]
            for d in ["conservative", "strict", "loose"]:
                p[f"duration_{d}"] = df[f"duration_{d}"].astype(float)
                p[f"event_{d}"] = df[f"observed_{d}"].astype(int)
        if key == "kr_en":
            p["death_without_year"] = df["death_without_year"]
            # 死亡年を実際に決めたソース (en_classifier の優先順位に合わせて排他にする)。
            # 特定のパーサの癖が 7 年の山を作っていないかを確かめるために持つ
            cat = df["cat_dissolved_year"].notna()
            ib = df["ya_end_year"].notna()
            p["src_category"] = cat.values
            p["src_infobox"] = (~cat & ib).values
            p["src_lead"] = (~cat & ~ib & df["death_year"].notna()).values
        panels[key] = p
    return panels


# --- 図 ---------------------------------------------------------------------

def plot_km(panels, path):
    """主分析と感度分析の生存曲線。ラベルは英語のみ。"""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    specs = [
        ("Main analysis (most complete source per country)",
         [("jp_ja", "Japan (ja.wikipedia)", "#1f77b4"),
          ("kr_en", "Korea (en.wikipedia)", "#d62728")]),
        ("Sensitivity: symmetric sources (en.wikipedia only)",
         [("jp_en", "Japan (en.wikipedia)", "#1f77b4"),
          ("kr_en", "Korea (en.wikipedia)", "#d62728")]),
    ]
    for ax, (title, series) in zip(axes, specs):
        for key, label, color in series:
            p = panels[key]
            kmf = sa.km_fit(p["duration"], p["event"], f"{label} (n={len(p)})")
            kmf.plot_survival_function(ax=ax, color=color, ci_alpha=0.12)
        ax.axvline(sa.CONTRACT_YEARS, color="gray", ls="--", lw=1)
        ax.text(sa.CONTRACT_YEARS + 0.2, 0.95, "7-year contract",
                fontsize=8, color="gray")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Years since formation")
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8, loc="lower left")
    axes[0].set_ylabel("Survival probability")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_hazard(panels, path):
    """離散時間ハザード。本研究の核心の図。"""
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for key, label, color in [("jp_ja", "Japan (ja.wikipedia)", "#1f77b4"),
                              ("jp_en", "Japan (en.wikipedia)", "#7fb3d5"),
                              ("kr_en", "Korea (en.wikipedia)", "#d62728")]:
        p = panels[key]
        # 表 5 (t = 1..12) と描画範囲を揃える。t >= 13 はリスク集合が薄く、
        # 図だけ先まで伸ばすと本文の表と読者の目に映る範囲がずれる。
        h = sa.discrete_hazard(p["duration"], p["event"], t_max=HAZARD_PLOT_TMAX)
        h = h[h["t"] >= 1]
        ax.plot(h["t"], h["hazard"], marker="o", ms=4, color=color,
                label=f"{label} (n={len(p)})")
        # 信頼区間は全系列に出す。1 群だけ帯を付けるとその群の山を
        # 強調しているように見えるため。
        ax.fill_between(h["t"], h["ci_low"], h["ci_high"],
                        color=color, alpha=0.10, linewidth=0)
    ax.axvline(sa.CONTRACT_YEARS, color="gray", ls="--", lw=1)
    # 注釈が枠外や凡例と重ならないよう、上端に余白を作ってから内側に置く
    top = ax.get_ylim()[1] * 1.18
    ax.set_ylim(0, top)
    ax.annotate("7-year standard\nexclusive contract (KR)",
                xy=(sa.CONTRACT_YEARS, top * 0.86),
                xytext=(sa.CONTRACT_YEARS - 0.3, top * 0.86),
                fontsize=8, color="gray", ha="right", va="top")
    ax.set_xlabel("Years since formation")
    ax.set_ylabel("Conditional hazard of dissolution")
    ax.set_title("Discrete-time hazard by year since formation", fontsize=10)
    ax.set_xticks(range(1, HAZARD_PLOT_TMAX + 1))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_by_sex(panels, path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, (key, title) in zip(axes, [("jp_ja", "Japan (ja.wikipedia)"),
                                       ("kr_en", "Korea (en.wikipedia)")]):
        p = panels[key]
        for sex, color in [("F", "#e377c2"), ("M", "#2ca02c")]:
            sub = p[p["sex"] == sex]
            if len(sub) < 20:
                continue
            kmf = sa.km_fit(sub["duration"], sub["event"],
                            f"{'Female' if sex == 'F' else 'Male'} (n={len(sub)})")
            kmf.plot_survival_function(ax=ax, color=color, ci_alpha=0.12)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Years since formation")
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8, loc="lower left")
    axes[0].set_ylabel("Survival probability")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    os.makedirs(PLOTS, exist_ok=True)
    panels = load_panels()

    lines = ["# Phase 5: 生存分析の結果", ""]
    lines += [
        "生成: `.venv/bin/python scripts/analyze_survival.py`",
        "",
        "生存時間は**年単位の整数** (結成年と解散年しか取れない)。"
        "打ち切り年 2026 で全グループを行政的に打ち切っている。",
        "",
    ]
    lines += rs.section_descriptive(panels, TIMES)
    lines += rs.section_km(panels, TIMES)
    lines += rs.section_logrank(panels)
    hazard_frames = []
    lines += rh.section_hazard(panels, hazard_frames)
    lines += rs.section_cox(panels)
    lines += rs.section_sensitivity(panels, TIMES)
    lines += rs.section_figures()

    plot_km(panels, os.path.join(PLOTS, "km_survival.png"))
    plot_hazard(panels, os.path.join(PLOTS, "hazard_by_year.png"))
    plot_by_sex(panels, os.path.join(PLOTS, "km_by_sex.png"))

    pd.concat(hazard_frames, ignore_index=True).to_csv(OUT_HAZARD, index=False)

    text = "\n".join(lines)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    print(f"\n-> {OUT_MD}")
    print(f"-> {OUT_HAZARD}")
    print(f"-> {PLOTS}/km_survival.png, hazard_by_year.png, km_by_sex.png")


if __name__ == "__main__":
    main()
