"""t = 7 の超過がモデルの置き方に依存しないかを検証する (査読指摘 6)。

  「baseline が cubic polynomial 一種類だけなのは弱い。natural spline、quadratic/cubic、
   あるいは year dummy を用いた柔軟な baseline で t=7 effect が残ることを示したい。
   さらに K-pop では同一 agency の群が独立とは考えにくいので、agency-clustered SE、
   frailty、あるいは leave-one-agency-out を追加すると…」

二つを測る:

A. **基準ハザードの関数形**を多項式 2-5 次 / 自然スプライン df=4-6 / 年ダミーに差し替えて、
   t = 7 の係数が残るか。年ダミーだけは原理的に識別できない (下記) ので、
   「できない」ことも結果として示す。

B. **所属先クラスタ**。同一事務所の群は独立でないので、クラスタロバスト SE と
   leave-one-cluster-out で係数が保つかを見る。韓国側は `agency` を持たないが
   `label` は持つので、これをクラスタの代理に使う (`src/label_en.py`)。

    .venv/bin/python scripts/probe_model_robustness.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import survival_analysis as sa  # noqa: E402
from label_en import primary_label  # noqa: E402
from wikitext import extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "results", "model_robustness.md")
KR_PAGES = os.path.join(ROOT, "data", "raw", "en_kr_pages.jsonl")
LABEL_FIELDS = ["label", "Label", "labels"]
FOCUS = 7
T_MAX = 15


def md_table(rows):
    if not rows:
        return ""
    cols = list(rows[0].keys())
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def fit(pp, baseline, cluster=None):
    """focus 項つきの離散時間ハザードモデルを当てる。

    baseline は patsy の式片。cluster を渡すとクラスタロバスト SE にする。
    """
    formula = f"event ~ {baseline} + focus"
    model = smf.glm(formula, data=pp,
                    family=sm.families.Binomial(link=sm.families.links.CLogLog()))
    if cluster is not None:
        return model.fit(cov_type="cluster", cov_kwds={"groups": cluster})
    return model.fit()


def summarize(res, label, n_clusters=None):
    if "focus" not in res.params.index:
        return {"基準ハザードの形": label, "ハザード比": "識別不能", "95% CI": "—", "p": "—"}
    b = res.params["focus"]
    se = res.bse["focus"]
    p = res.pvalues["focus"]
    lo, hi = np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)
    row = {
        "基準ハザードの形": label,
        "ハザード比": f"{np.exp(b):.2f}",
        "95% CI": f"{lo:.2f}–{hi:.2f}" if np.isfinite(hi) and hi < 1e4 else "推定不能 (発散)",
        "p": f"{p:.3f}" if np.isfinite(p) else "—",
    }
    if n_clusters is not None:
        row["クラスタ数"] = n_clusters
    return row


def load_kr_labels():
    """記事タイトル -> 所属先 (label 由来) の対応。"""
    out = {}
    with open(KR_PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing"):
                continue
            out[rec["title"]] = primary_label(
                extract_field(rec.get("wikitext", ""), LABEL_FIELDS))
    return out


def main():
    kr = pd.read_parquet(os.path.join(ROOT, "data", "kr_en_survival.parquet"))
    kr = kr.rename(columns={"observed": "event"}) if "observed" in kr.columns else kr
    labels = load_kr_labels()
    kr["cluster"] = kr["group_id"].map(labels)

    pp = sa.person_period(kr, "duration", "event", t_max=T_MAX, keep=("group_id", "cluster"))
    pp["focus"] = (pp["t"] == FOCUS).astype(int)

    lines = ["# t = 7 の超過はモデルの置き方に依存するか", ""]
    lines.append("査読指摘 6 への対応。韓国 en.wikipedia パネル (n = "
                 f"{len(kr)}) の person-period {len(pp):,} 行で推定。")
    lines.append("")

    # --- A. 基準ハザードの関数形 -------------------------------------------
    specs = [
        ("2 次多項式", "I(t**1) + I(t**2)"),
        ("3 次多項式 (主分析)", "I(t**1) + I(t**2) + I(t**3)"),
        ("4 次多項式", "I(t**1) + I(t**2) + I(t**3) + I(t**4)"),
        ("5 次多項式", "I(t**1) + I(t**2) + I(t**3) + I(t**4) + I(t**5)"),
        ("自然スプライン df=4", "cr(t, df=4)"),
        ("自然スプライン df=5", "cr(t, df=5)"),
        ("自然スプライン df=6", "cr(t, df=6)"),
        ("年ダミー (飽和)", "C(t)"),
    ]
    rows = []
    for label, baseline in specs:
        try:
            res = fit(pp, baseline)
            rows.append(summarize(res, label))
        except Exception as e:  # noqa: BLE001
            rows.append({"基準ハザードの形": label, "ハザード比": "推定失敗",
                         "95% CI": str(e)[:40], "p": "—"})

    lines.append("## A. 基準ハザードの関数形を変える")
    lines.append("")
    lines.append(md_table(rows))
    lines.append("")
    lines.append(
        "> **年ダミーだけは原理的に識別できない**。基準ハザードを `C(t)` で完全に自由にすると "
        "`1{t = 7}` はその一水準と完全に重なり、「超過」を定義する余地が残らない。"
        "査読で提案された 3 つの形のうち、多項式とスプラインは実行できるが、"
        "年ダミーは**平滑性の仮定を置かない限り超過という概念自体が成立しない**ことを示している。"
    )
    lines.append("")

    # --- B. 所属先クラスタ ---------------------------------------------------
    have = pp["cluster"].notna()
    pp_c = pp[have].copy()
    n_groups = kr["cluster"].notna().sum()
    n_clusters = kr.loc[kr["cluster"].notna(), "cluster"].nunique()
    sizes = kr.loc[kr["cluster"].notna(), "cluster"].value_counts()

    lines.append("## B. 同一事務所の群が独立でないことへの対応")
    lines.append("")
    lines.append(
        f"韓国側 en.wikipedia は `agency` フィールドを **1 件も持たない** (実測 0/641) が、"
        f"`label` は持つ。K-pop は制作事務所がそのままレーベルであることが多いので、"
        f"label を所属クラスタの代理に使う。母集団 {len(kr)} 件のうち "
        f"**{n_groups} 件 ({n_groups/len(kr):.1%}) に所属先が付き、{n_clusters} クラスタ**に分かれる。"
        f"最大クラスタでも {int(sizes.max())} 群なので、少数の事務所が結果を決めていないかは"
        f"下の leave-one-cluster-out で確かめる。"
    )
    lines.append("")

    base3 = "I(t**1) + I(t**2) + I(t**3)"
    rows_b = []
    rows_b.append(summarize(fit(pp, base3), "全群・独立と仮定 (主分析)"))
    rows_b.append(summarize(fit(pp_c, base3), "所属先が判る群のみ・独立と仮定"))
    rows_b.append(summarize(fit(pp_c, base3, cluster=pp_c["cluster"]),
                            "所属先が判る群のみ・**クラスタロバスト SE**", n_clusters))
    lines.append(md_table(rows_b))
    lines.append("")

    # leave-one-cluster-out: 大きいクラスタを 1 つずつ抜く
    top = sizes.head(8).index.tolist()
    rows_l = []
    for c in top:
        sub = pp_c[pp_c["cluster"] != c]
        res = fit(sub, base3, cluster=sub["cluster"])
        r = summarize(res, f"{c} を除外 (n = {int(sizes[c])} 群)")
        rows_l.append(r)
    lines.append("### leave-one-cluster-out (規模上位 8 事務所を 1 つずつ除外)")
    lines.append("")
    lines.append(md_table(rows_l))
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
