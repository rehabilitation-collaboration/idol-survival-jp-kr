"""Phase 5 のレポート生成 (計算は survival_analysis.py・組み立てはここ)。

各関数は Markdown の行リストを返す。`scripts/analyze_survival.py` が並べる。
7 年ハザード集中の節だけは分量が大きいので `report_hazard.py` に分けてある。
"""
import numpy as np
import pandas as pd

import survival_analysis as sa
from report_common import LABELS, fmt_p as _fmt_p


# --- 1. 記述統計 ------------------------------------------------------------

def section_descriptive(panels, times):
    a = ["## 1. 母集団と打ち切り", ""]
    a += ["| 母集団 | n | 死亡 | 打ち切り | 死亡率 | 生存期間中央値 |", "|---|---|---|---|---|---|"]
    for key in ["jp_ja", "kr_en", "jp_en"]:
        p = panels[key]
        d = int(p["event"].sum())
        med = sa.median_survival(p["duration"], p["event"])
        med_s = f"{med:.1f} 年" if np.isfinite(med) else "未到達"
        a.append(f"| {LABELS[key]} | {len(p)} | {d} | {len(p) - d} | {d / len(p):.1%} | {med_s} |")
    a += ["", "生存期間中央値は Kaplan-Meier の S(t) = 0.5 到達点。"
          "打ち切りが多いため到達しない母集団がある。", ""]

    a += ["### 性別の内訳", ""]
    a += ["| 母集団 | F | M | mixed | unknown | 判明率 |", "|---|---|---|---|---|---|"]
    for key in ["jp_ja", "kr_en", "jp_en"]:
        s = panels[key]["sex"]
        v = s.value_counts()
        a.append("| {} | {} | {} | {} | {} | {:.1%} |".format(
            LABELS[key], v.get("F", 0), v.get("M", 0), v.get("mixed", 0),
            v.get("unknown", 0), (s != "unknown").mean()))
    a.append("")
    # 英語版の性別はカテゴリとリード文の 2 ソースから導出している。
    # 一致率は最終母集団で測り直す (シード全体の値を流用しない)
    for key in ["kr_en", "jp_en"]:
        p = panels[key]
        both = p[p["sex_cat"].notna() & p["sex_lead"].notna()]
        agree = (both["sex_cat"] == both["sex_lead"]).mean()
        a.append(f"- {LABELS[key]}: 2 ソースが両方とも取れた {len(both)} 件で"
                 f"**一致率 {agree:.1%}** (カテゴリを優先し、リード文は補助)")
    a += ["", "※ 日本語版 (ja) の性別はカテゴリと冒頭定義文から Phase 1 で導出済み "
          "(`src/idol_classifier.py`)。英語版とは導出経路が違う。", ""]

    a += ["### コホート別 (デビュー年 5 年区切り)", ""]
    a += ["| コホート | 日本 n (死亡) | 韓国 n (死亡) |", "|---|---|---|"]
    for c in sa.COHORT_LABELS:
        j = panels["jp_ja"][panels["jp_ja"]["cohort"] == c]
        k = panels["kr_en"][panels["kr_en"]["cohort"] == c]
        a.append(f"| {c} | {len(j)} ({int(j['event'].sum())}) | {len(k)} ({int(k['event'].sum())}) |")
    a.append("")
    return a


# --- 2. Kaplan-Meier --------------------------------------------------------

def section_km(panels, times):
    a = ["## 2. Kaplan-Meier 生存曲線", ""]
    a += ["経過年ごとの**離脱率** (1 - S(t))。括弧内は 95% 信頼区間。", ""]
    header = "| 経過年 | " + " | ".join(LABELS[k] for k in ["jp_ja", "kr_en", "jp_en"]) + " |"
    a += [header, "|---|---|---|---|"]
    tabs = {k: sa.km_at(panels[k]["duration"], panels[k]["event"], times)
            for k in ["jp_ja", "kr_en", "jp_en"]}
    for i, t in enumerate(times):
        cells = []
        for k in ["jp_ja", "kr_en", "jp_en"]:
            r = tabs[k].iloc[i]
            cells.append(f"{r['exit']:.1%} ({1 - r['ci_high']:.1%}–{1 - r['ci_low']:.1%})")
        a.append(f"| {t} 年 | " + " | ".join(cells) + " |")
    a.append("")

    j3 = tabs["jp_ja"].iloc[times.index(3)]
    k3 = tabs["kr_en"].iloc[times.index(3)]
    e3 = tabs["jp_en"].iloc[times.index(3)]
    a += [
        f"- **主分析どうしの 3 年離脱率はほぼ一致**: 日本 {j3['exit']:.1%} vs 韓国 {k3['exit']:.1%} "
        f"(差 {(j3['exit'] - k3['exit']) * 100:+.1f} pt)・信頼区間も重なる",
        f"- **英語版で揃えると日本が長命に見える**: 日本 {e3['exit']:.1%} vs 韓国 {k3['exit']:.1%} "
        f"(差 {(e3['exit'] - k3['exit']) * 100:+.1f} pt)",
        "",
        "> ⚠️ この食い違いを日韓差と読んではいけない。英語版のカバー率が日本 22.6% / "
        "韓国 46.4% と倍近く違い、同一ソースにしてもバイアス条件は揃っていない "
        "(Phase 3 `results/method_validation.md`)。",
        "",
        f"- Kim (2026) の公表値 (3 年以内 約 45%) との差は韓国側で "
        f"**{(k3['exit'] - 0.45) * 100:+.1f} pt**。Phase 3 の分岐条件が発動した状態は変わらない",
        "",
    ]
    return a


# --- 3. log-rank ------------------------------------------------------------

def section_logrank(panels):
    a = ["## 3. log-rank 検定", ""]
    a += ["| 比較 | 母集団 | χ² | df | p |", "|---|---|---|---|---|"]

    def add(label, df, col, note):
        r = sa.logrank(df, col, "duration", "event")
        a.append(f"| {label} | {note} | {r['test_statistic']:.2f} | {r['df']} | {_fmt_p(r['p_value'])} |")

    pooled_main = pd.concat([panels["jp_ja"], panels["kr_en"]], ignore_index=True)
    pooled_en = pd.concat([panels["jp_en"], panels["kr_en"]], ignore_index=True)
    add("日韓 (主分析・ソース非対称)", pooled_main, "country", f"n={len(pooled_main)}")
    add("日韓 (感度分析・英語版で対称化)", pooled_en, "country", f"n={len(pooled_en)}")
    for key in ["jp_ja", "kr_en"]:
        p = panels[key]
        sub = p[p["sex"].isin(["F", "M"])]
        add(f"男女 ({LABELS[key]})", sub, "sex", f"n={len(sub)}")
        add(f"コホート ({LABELS[key]})", p.dropna(subset=["cohort"]).assign(
            cohort=lambda d: d["cohort"].astype(str)), "cohort", f"n={len(p)}")
    a.append("")
    a += [
        "> **主分析どうしの日韓比較 (1 行目) はソースが非対称なので、有意でも無意味**。"
        "日韓差の判断に使えるのは 2 行目だが、そちらもカバー率が揃っていない。",
        "",
    ]
    return a


# --- 5. Cox -----------------------------------------------------------------

def _cox_table(cph, title, a):
    a += [f"#### {title}", "", "| 共変量 | ハザード比 | 95% CI | p |", "|---|---|---|---|"]
    s = cph.summary
    for name, r in s.iterrows():
        a.append(f"| `{name}` | {r['exp(coef)']:.2f} | "
                 f"{r['exp(coef) lower 95%']:.2f}–{r['exp(coef) upper 95%']:.2f} | "
                 f"{_fmt_p(r['p'])} |")
    a += ["", f"n = {len(cph.event_observed)} / イベント = {int(cph.event_observed.sum())} / "
          f"concordance = {cph.concordance_index_:.3f}", ""]
    return a


def section_cox(panels):
    a = ["## 5. Cox 比例ハザードモデル", ""]
    a += ["生存時間は年単位の整数なので同順位が多い。lifelines 既定の Efron 近似で扱い、"
          "duration = 0 を避けるため全体を +0.5 年ずらして当てている "
          "(区間 [t, t+1) の中点をとる慣行)。", ""]

    # モデル A: 英語版で対称化した日韓プール
    pooled = pd.concat([panels["jp_en"], panels["kr_en"]], ignore_index=True)
    pooled = pooled.dropna(subset=["cohort"]).copy()
    pooled["cohort"] = pooled["cohort"].astype(str)
    d = pooled[["duration", "event", "country", "sex", "cohort"]]
    cph_a, fit_df_a = sa.cox_fit(d, "country + sex + cohort")
    a += ["### モデル A: 日韓プール (英語版で対称化)", "",
          "PLAN の共変量のうち**国・性別**を入れる。事務所は韓国側の英語版 Infobox に"
          "対応するフィールドが無いため、このモデルでは使えない。", ""]
    _cox_table(cph_a, "推定結果 (参照: 国=JP / 性別=F / コホート=1996-2000)", a)

    # モデル B: 日本 ja 版 (事務所規模つき)
    jp = panels["jp_ja"].dropna(subset=["cohort"]).copy()
    jp["cohort"] = jp["cohort"].astype(str)
    d2 = jp[["duration", "event", "sex", "cohort", "agency_class"]]
    cph_b, fit_df_b = sa.cox_fit(d2, "sex + cohort + agency_class")
    a += ["### モデル B: 日本 (ja.wikipedia・事務所規模つき)", "",
          "**事務所規模**は「母集団内で同じ事務所に属するグループ数」で測る。"
          "手作りの事務所リストを持ち込まずに済む一方、観測窓 30 年分の累積なので"
          "長く存続した事務所ほど大きく出る粗い代理指標である。"
          f"Infobox に事務所フィールドが無い {(jp['agency_class'] == 'unknown').mean():.1%} は"
          "落とさず `unknown` 水準として残した "
          "(落とすと記事の薄いグループが系統的に消え、記事化バイアスと同じ向きに歪む)。", ""]
    _cox_table(cph_b, "推定結果 (参照: 性別=F / コホート=1996-2000 / 事務所規模=1 組)", a)

    a += ["> **RIAJ 認定を共変量に入れていない**。認定は結成後に決まるうえ、"
          "長く続いたグループほど認定機会が増えるので、生存への逆因果が入る "
          "(immortal time bias)。Phase 4 で測った認定別の離脱率は記述統計として"
          "報告するに留める。", "",
          "> ⚠️ **`sex[T.unknown]` と `agency_class[T.unknown]` は交絡の塊であって、"
          "解釈してはいけない**。これらは「記事にその情報が書かれていない」という"
          "欠損の指標であり、記事の充実度 (= 知名度) と直結する。"
          "Phase 4 で記事が薄いグループほど短命だと分かっているので、"
          "係数は性別や事務所規模の効果ではなく記事化バイアスを拾っている。"
          "モデルに残しているのは、落とすと母集団が知名度で選抜されて"
          "他の係数まで歪むため。", ""]

    # Schoenfeld
    a += ["### 比例ハザード仮定の検定 (Schoenfeld 残差)", ""]
    for title, cph, fdf in [("モデル A", cph_a, fit_df_a), ("モデル B", cph_b, fit_df_b)]:
        res = sa.schoenfeld(cph, fdf)
        a += [f"#### {title}", "", "| 共変量 | χ² | p |", "|---|---|---|"]
        summ = res.summary
        for name, r in summ.iterrows():
            a.append(f"| `{name}` | {r['test_statistic']:.2f} | {_fmt_p(r['p'])} |")
        violated = [n for n, r in summ.iterrows() if r["p"] < 0.05]
        a += ["", ("→ **仮定を満たさない共変量あり**: " + ", ".join(f"`{v}`" for v in violated)
                   if violated else "→ 全ての共変量で仮定は棄却されない"), ""]
    a += ["> 比例ハザード仮定が破れている共変量については、Cox のハザード比は"
          "観測期間全体の平均としてしか読めない。時点別の構造は §4 の"
          "離散時間ハザードで直接見ること。", ""]
    return a


# --- 6. 感度分析 ------------------------------------------------------------

def section_sensitivity(panels, times):
    a = ["## 6. 感度分析", ""]

    a += ["### 6.1 死亡定義 3 種 (日本 ja.wikipedia)", "",
          "| 定義 | 死亡 | 3 年離脱率 | 5 年 | 7 年 | 10 年 |", "|---|---|---|---|---|---|"]
    jp = panels["jp_ja"]
    exit3 = {}
    for d, label in [("conservative", "保守 (解散カテゴリのみ)"),
                     ("strict", "**厳格 (主分析)**"),
                     ("loose", "緩和 (+ リード文の休止)")]:
        t = sa.km_at(jp[f"duration_{d}"], jp[f"event_{d}"].astype(bool), [3, 5, 7, 10])
        exit3[d] = t.iloc[0]["exit"]
        a.append(f"| {label} | {int(jp[f'event_{d}'].sum())} | " +
                 " | ".join(f"{r['exit']:.1%}" for _, r in t.iterrows()) + " |")
    kr3 = sa.km_at(panels["kr_en"]["duration"], panels["kr_en"]["event"], [3]).iloc[0]["exit"]
    span = (exit3["loose"] - exit3["conservative"]) * 100
    a += ["", f"→ 3 年離脱率は定義によって **{exit3['conservative']:.1%} - {exit3['loose']:.1%}** "
          f"の幅で動く (最大 {span:.1f} pt)。", ""]
    a += ["> ⚠️ **日韓の大小関係は定義に依存する**。韓国側は死亡定義が 1 種類しかなく、"
          f"内容は日本の厳格定義に近い。厳格どうしなら日本 {exit3['strict']:.1%} vs "
          f"韓国 {kr3:.1%} でほぼ並ぶが、日本を保守定義にすると "
          f"{exit3['conservative']:.1%} vs {kr3:.1%} で日本が "
          f"{(kr3 - exit3['conservative']) * 100:.1f} pt 低く見える。"
          "**定義を揃えずに日韓を比べてはいけない**。", ""]

    a += ["### 6.2 観測窓", "",
          "| 観測窓 | 日本 n | 3 年離脱率 | 韓国 n | 3 年離脱率 |", "|---|---|---|---|---|"]
    for w, label in [(sa.WINDOW_MAIN, "1996-2025 (**主分析**)"),
                     (sa.WINDOW_STABLE, "2009-2025 (感度 A: 年 30 件以上)"),
                     (sa.WINDOW_NOLAG, "1996-2022 (感度 B: 記事化ラグ除去)")]:
        cells = []
        for key in ["jp_ja", "kr_en"]:
            p = panels[key]
            sub = p[p["formed_year"].between(*w)]
            t = sa.km_at(sub["duration"], sub["event"], [3])
            cells += [str(len(sub)), f"{t.iloc[0]['exit']:.1%}"]
        a.append(f"| {label} | " + " | ".join(cells) + " |")
    a += ["", "→ 窓を変えても日韓の 3 年離脱率はほぼ並ぶ。"
          "記事化ラグを除く窓 B で両国とも離脱率が上がるのは、"
          "直近コホートの打ち切りが外れるため。", ""]

    a += ["### 6.3 アイドル判定ルール (ダンス&ボーカル系を外す)", ""]
    sub = jp[~jp["definition_sensitive"]]
    t_all = sa.km_at(jp["duration"], jp["event"], [3, 5, 7])
    t_sub = sa.km_at(sub["duration"], sub["event"], [3, 5, 7])
    a += ["| 母集団 | n | 3 年 | 5 年 | 7 年 |", "|---|---|---|---|---|"]
    a.append(f"| ルール D (主分析) | {len(jp)} | " +
             " | ".join(f"{r['exit']:.1%}" for _, r in t_all.iterrows()) + " |")
    a.append(f"| 定義感応ケースを除外 | {len(sub)} | " +
             " | ".join(f"{r['exit']:.1%}" for _, r in t_sub.iterrows()) + " |")
    n_sens = len(jp) - len(sub)
    a += ["", f"→ 定義感応 {n_sens} 件 ({n_sens / len(jp):.1%}) を外しても、"
          f"3 年離脱率の動きは {abs(t_sub.iloc[0]['exit'] - t_all.iloc[0]['exit']) * 100:.1f} pt "
          "にとどまる。", ""]

    a += ["### 6.4 韓国: 死亡と分かるが年が特定できない 46 件", ""]
    kr = panels["kr_en"]
    sub = kr[~kr["death_without_year"]]
    a += ["| 母集団 | n | 3 年 | 5 年 | **7 年ハザード比** | p |", "|---|---|---|---|---|---|"]
    for label, d in [("主分析 (打ち切り扱い)", kr), ("年不明の死亡を除外", sub)]:
        t = sa.km_at(d["duration"], d["event"], [3, 5])
        r = sa.excess_hazard_test(d["duration"], d["event"])
        a.append(f"| {label} | {len(d)} | " +
                 " | ".join(f"{x['exit']:.1%}" for _, x in t.iterrows()) +
                 f" | {r['ratio']:.2f} | {_fmt_p(r['p_value'])} |")
    a += ["", "→ 年不明の死亡を除いても **7 年の超過は残る**。"
          "この 46 件が 7 年の山を作っているわけではない。", ""]
    return a


def section_figures():
    return [
        "## 7. 図",
        "",
        "| ファイル | 内容 |",
        "|---|---|",
        "| `plots/km_survival.png` | Kaplan-Meier 生存曲線 (主分析 / 英語版で対称化) |",
        "| `plots/hazard_by_year.png` | **離散時間ハザード。7 年地点の集中を示す本命の図** |",
        "| `plots/km_by_sex.png` | 男女別の生存曲線 (日韓) |",
        "",
        "図中のラベルは英語のみ (PDF 生成時の CJK 問題を避けるため)。",
        "",
    ]
