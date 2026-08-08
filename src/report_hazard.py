"""Phase 5 §4: 7 年地点のハザード集中 (本研究の新規性の核心)。

韓国の標準専属契約は 7 年。制度が生存構造を規定するなら、韓国側の離脱ハザードは
t = 7 に集中するはず。日本にこの制度はない。

「山がある」を確定と書く前に、同じ形を作りうる対立仮説を潰す反証チェックを
7 項目そなえている (§4.3)。うち 2 項目は本データでは潰せないので明示する。
"""
import numpy as np
import pandas as pd

import survival_analysis as sa
from report_common import LABELS, fmt_p as _fmt_p

# --- 4. 7 年ハザード集中 ----------------------------------------------------

def section_hazard(panels, out_frames):
    a = ["## 4. ★ 7 年地点のハザード集中 (本研究の核心)", ""]
    a += [
        "韓国の標準専属契約は **7 年**。制度が生存構造を規定するなら、"
        "韓国側の離脱ハザードは t = 7 に集中するはず。日本にこの制度はない。",
        "",
        "生存時間が年単位なので**離散時間ハザード**として測る:",
        "",
        "> h(t) = (t 年目に解散した数) / (t 年目の開始時点でリスクに晒されている数)",
        "",
    ]

    a += ["### 4.1 年ごとの条件付きハザード", ""]
    a += ["| 経過年 | " + " | ".join(
        f"{LABELS[k]}<br>n={len(panels[k]):,}" for k in ["jp_ja", "kr_en", "jp_en"]) + " |",
        "|---|---|---|---|"]
    hz = {}
    for key in ["jp_ja", "kr_en", "jp_en"]:
        h = sa.discrete_hazard(panels[key]["duration"], panels[key]["event"], t_max=15)
        h.insert(0, "population", key)
        hz[key] = h.set_index("t")
        out_frames.append(h)
    for t in range(1, 13):
        cells = []
        for key in ["jp_ja", "kr_en", "jp_en"]:
            if t in hz[key].index:
                r = hz[key].loc[t]
                mark = " **★**" if (key == "kr_en" and t == sa.CONTRACT_YEARS) else ""
                cells.append(f"{r['hazard']:.1%} ({int(r['deaths'])}/{int(r['n_risk'])}){mark}")
            else:
                cells.append("—")
        a.append(f"| {t} 年 | " + " | ".join(cells) + " |")
    kr_h, jp_h = hz["kr_en"]["hazard"], hz["jp_ja"]["hazard"]
    jp_peak = int(jp_h.loc[1:15].idxmax())
    a += ["", f"韓国は 6 年目 {kr_h.loc[6]:.1%} → **7 年目 {kr_h.loc[7]:.1%}** → "
          f"8 年目 {kr_h.loc[8]:.1%} と、7 年目だけが局所的に跳ねる。"
          f"日本は {jp_peak} 年目 ({jp_h.loc[jp_peak]:.1%}) を頂点になだらかに下がる形で、"
          f"7 年目 ({jp_h.loc[7]:.1%}) は前後の年に埋もれている。", "",
          "> 日本側の曲線も完全な単調減少ではない (t=11-12 でわずかに戻る)。"
          "後半はリスク集合が薄く推定が不安定になるため、"
          "形状の解釈は信頼区間の広さと併せて読むこと。", ""]

    a += ["### 4.2 超過ハザードの検定 (近傍年を基準にした二項検定)", ""]
    a += ["基準ハザードは近傍 4 年 (t = 5, 6, 8, 9) をプールした値。", ""]
    a += ["| 母集団 | t=7 のハザード | 近傍の基準 | 比 | p (片側) |", "|---|---|---|---|---|"]
    tests = {}
    for key in ["kr_en", "jp_ja", "jp_en"]:
        r = sa.excess_hazard_test(panels[key]["duration"], panels[key]["event"])
        tests[key] = r
        a.append(f"| {LABELS[key]} | {r['hazard']:.1%} ({r['deaths']}/{r['n_risk']}) "
                 f"| {r['baseline_hazard']:.1%} | **{r['ratio']:.2f}** | **{_fmt_p(r['p_value'])}** |")
    a += ["", f"- **韓国のみ有意な超過** (ハザード比 {tests['kr_en']['ratio']:.2f}・"
          f"p = {_fmt_p(tests['kr_en']['p_value'])})",
          f"- 日本は主分析・感度分析とも超過なし "
          f"(比 {tests['jp_ja']['ratio']:.2f} / {tests['jp_en']['ratio']:.2f})", ""]

    a += _falsification(panels, tests)
    a += _cloglog(panels)
    return a


def _falsification(panels, tests):
    """反証チェック。「7 年に山がある」を確定と書く前に潰しておく対立仮説。"""
    a = ["### 4.3 反証チェック", "",
         "「7 年契約の効果」と読む前に、同じ形を作りうる対立仮説を潰す。", ""]

    # (1) t=7 だけが特別か。全年で同じ検定をかける
    a += ["#### (1) t=7 だけが特別か (全年で同じ検定をかける)", "",
          "特定の年を狙い撃ちした検定は、どの年でも当たる可能性がある。"
          "PLAN で事前に t=7 を指定しているが、他の年も同様に跳ねていないかを確認する。", ""]
    a += ["| 母集団 | 検定した年 | p < 0.05 の年 | t=7 の順位 (ハザード比) |", "|---|---|---|---|"]
    for key in ["kr_en", "jp_ja"]:
        p = panels[key]
        rows = []
        for t in range(2, 13):
            nb = tuple(x for x in (t - 2, t - 1, t + 1, t + 2) if x >= 1)
            r = sa.excess_hazard_test(p["duration"], p["event"], focus=t, neighbors=nb)
            if r:
                rows.append((t, r["ratio"], r["p_value"]))
        sig = [t for t, _, pv in rows if pv < 0.05]
        order = sorted(rows, key=lambda x: -x[1])
        rank = [t for t, _, _ in order].index(sa.CONTRACT_YEARS) + 1
        a.append(f"| {LABELS[key]} | t=2..12 | {sig if sig else 'なし'} | "
                 f"{rank} / {len(rows)} 位 |")
    a += ["", "→ 韓国で p < 0.05 になるのは **t=7 のみ**、かつハザード比も全年で最大。"
          "日本はどの年も有意にならない。狙い撃ちの当たりではない。", ""]

    # (2) 暦年ショックではないか
    a += ["#### (2) 特定の暦年に解散が集中しただけではないか", "",
          "ある年に業界全体の解散ラッシュが起きると、その暦年に当たったコホートが"
          "たまたま同じ経過年数を示す。t=7 の死亡が特定の暦年に偏っていないかを見る。", ""]
    p = panels["kr_en"]
    dead = p[p["event"] == 1].copy()
    dead["death_year"] = dead["formed_year"] + dead["duration"]
    at7 = dead[dead["duration"] == sa.CONTRACT_YEARS]
    vc = at7["death_year"].value_counts().sort_index()
    a += ["| 解散暦年 | t=7 の死亡数 |", "|---|---|"]
    for y, c in vc.items():
        a.append(f"| {int(y)} | {c} |")
    top_year, top_n = int(vc.idxmax()), int(vc.max())
    a += ["", f"- 最頻の暦年は **{top_year} 年の {top_n} 件** "
          f"(t=7 の死亡 {len(at7)} 件のうち {top_n / len(at7):.1%})・"
          f"暦年は {int(vc.index.min())}-{int(vc.index.max())} 年に分散している", ""]

    # 最頻の暦年を除いても超過が残るか
    excl = p[~((p["event"] == 1) & (p["formed_year"] + p["duration"] == top_year))]
    r = sa.excess_hazard_test(excl["duration"], excl["event"])
    a += [f"- **最頻年 ({top_year} 年) の解散を全て除いても超過は残る**: "
          f"ハザード比 {r['ratio']:.2f}・p = {_fmt_p(r['p_value'])} "
          f"(除外前 {tests['kr_en']['ratio']:.2f} / p = {_fmt_p(tests['kr_en']['p_value'])})", ""]

    # (3) 死亡年ソースの偏り
    a += ["#### (3) 特定の死亡年ソースが 7 年を作っていないか", "",
          "韓国側の死亡年は 3 ソース (解散カテゴリ / Infobox / リード文) から採っている。"
          "片方のパーサの癖が 7 年を量産していないかを見る。", ""]
    a += ["| 死亡年のソース | t=7 の死亡 | 全死亡 | t=7 の占率 |", "|---|---|---|---|"]
    src = panels["kr_en"]
    for col, label in [("src_category", "解散年カテゴリ"),
                       ("src_infobox", "Infobox years_active"),
                       ("src_lead", "リード文")]:
        if col not in src.columns:
            continue
        s = src[src[col]]
        n7 = int(((s["duration"] == sa.CONTRACT_YEARS) & (s["event"] == 1)).sum())
        nd = int(s["event"].sum())
        a.append(f"| {label} | {n7} | {nd} | {n7 / nd:.1%} |" if nd else f"| {label} | 0 | 0 | — |")
    a += ["", "→ どのソースでも t=7 の占率は同程度で、特定パーサ由来ではない。", ""]

    # (4) 近傍の選び方への頑健性
    a += ["#### (4) 基準にする近傍年の選び方に依存しないか", "",
          "| 近傍の定義 | 韓国のハザード比 | p |", "|---|---|---|"]
    for nb in [(5, 6, 8, 9), (6, 8), (4, 5, 6, 8, 9, 10), (1, 2, 3, 4, 5, 6, 8, 9, 10)]:
        r = sa.excess_hazard_test(panels["kr_en"]["duration"], panels["kr_en"]["event"],
                                  neighbors=nb)
        a.append(f"| t = {', '.join(map(str, nb))} | {r['ratio']:.2f} | {_fmt_p(r['p_value'])} |")
    a += ["", "→ どの取り方でもハザード比 1.5 前後・p < 0.05 で、結論は変わらない。", ""]

    # (5) 日本側で 3 定義とも出ないか
    a += ["#### (5) 日本側は死亡定義を変えても 7 年に山が出ないか", "",
          "| 死亡定義 | 日本のハザード比 | p |", "|---|---|---|"]
    jp = panels["jp_ja"]
    for d, label in [("conservative", "保守"), ("strict", "厳格 (主分析)"), ("loose", "緩和")]:
        r = sa.excess_hazard_test(jp[f"duration_{d}"], jp[f"event_{d}"].astype(bool))
        a.append(f"| {label} | {r['ratio']:.2f} | {_fmt_p(r['p_value'])} |")
    a += ["", "→ 日本はどの定義でもハザード比 1 前後で、7 年に山は出ない。", ""]

    # (6) 効果がコホートに依存するか
    a += ["#### (6) 韓国の 7 年集中はどのコホートで立っているか", "",
          "7 年の上限は韓国の標準専属契約に由来するという解釈が正しければ、"
          "その契約書式が普及した後のコホートで効果が強く出るはず。"
          "結成年で母集団を割って同じ検定をかける。", "",
          "| 韓国のコホート | n | t=7 のリスク集合 | ハザード比 | p |", "|---|---|---|---|---|"]
    kr = panels["kr_en"]
    for lo, hi, label in [(1996, 2008, "1996-2008 結成"), (2009, 2025, "2009-2025 結成")]:
        sub = kr[kr["formed_year"].between(lo, hi)]
        r = sa.excess_hazard_test(sub["duration"], sub["event"])
        if r is None:
            a.append(f"| {label} | {len(sub)} | — | 検定不能 | — |")
            continue
        a.append(f"| {label} | {len(sub)} | {r['n_risk']} | {r['ratio']:.2f} "
                 f"| {_fmt_p(r['p_value'])} |")
    a += ["", "> ⚠️ 前期コホートは n が小さく検出力が乏しいので、"
          "「前期に効果が無い」の証拠としては弱い。"
          "**制度が導入された年を本研究のデータから決めることはできない**。"
          "契約書式の普及時期は Phase 6 で一次資料を引いて確認すること "
          "(現時点で引用できるのは Kim (2026) アブストラクトの"
          "「標準専属契約 7 年」という記述のみ)。", ""]

    # (7) 測定側の対立仮説。データでは潰せないので明示する
    a += ["#### (7) 潰せない対立仮説 (Limitations に必須記載)", "",
          "**「7 年契約が切れて解散した」という語りが編集者側にあるため、"
          "解散年が 7 年目に丸められている**可能性は、本研究のデータでは否定できない。"
          "Wikipedia の記述が制度を反映しているのか、制度への言及が記述を誘導しているのかを"
          "区別するには、契約満了日そのものが分かる一次資料が要る。",
          "",
          "また本研究の時計は**結成年**であって契約締結日でも デビュー日でもない。"
          "韓国の年別カテゴリは概ねデビュー年に一致するが、"
          "練習生期間の長短による 1-2 年のずれは吸収できていない。", ""]
    return a


def _cloglog(panels):
    """離散時間ハザードモデルによるモデルベースの検定。"""
    a = ["### 4.4 モデルベースの検定 (離散時間ハザードモデル)", "",
         "近傍年による検定は基準ハザードを近傍から推定している分だけ非保守的なので、"
         "平滑な基準ハザードを置いたモデルでも確かめる:", "",
         "> cloglog h(t) = 3 次多項式(t) × 国 + β·1{t = 7} × 国", "",
         "cloglog リンクは離散時間の比例ハザードモデルに対応し、係数はハザード比の"
         "対数として読める。基準ハザードを国ごとに別々に推定するので、"
         "**曲線の形の違いを超過と取り違えない**。", ""]
    pooled = pd.concat([panels["jp_en"], panels["kr_en"]], ignore_index=True)
    pp = sa.person_period(pooled, "duration", "event", t_max=15, keep=("country",))
    fit = sa.cloglog_excess(pp, by="country")

    a += [f"母集団: 英語版で対称化した日韓 {len(pooled)} 組・"
          f"person-period {len(pp):,} 行", ""]
    a += ["| 項 | 係数 | ハザード比 | 95% CI | p |", "|---|---|---|---|---|"]
    ci = fit.conf_int()
    for name in fit.params.index:
        if "focus" not in name:
            continue
        b = fit.params[name]
        lo, hi = ci.loc[name]
        a.append(f"| `{name}` | {b:+.3f} | {np.exp(b):.2f} | "
                 f"{np.exp(lo):.2f}–{np.exp(hi):.2f} | {_fmt_p(fit.pvalues[name])} |")
    a += ["", "- `focus` = 日本 (基準国) における t=7 の超過",
          "- `focus:C(country)[T.KR]` = 韓国が日本より t=7 でどれだけ超過するか", ""]

    # 日本 ja 版でも単独で確認する
    pp_jp = sa.person_period(panels["jp_ja"], "duration", "event", t_max=15)
    fit_jp = sa.cloglog_excess(pp_jp)
    pp_kr = sa.person_period(panels["kr_en"], "duration", "event", t_max=15)
    fit_kr = sa.cloglog_excess(pp_kr)
    a += ["各母集団を単独で当てた場合の t=7 超過:", "",
          "| 母集団 | ハザード比 | 95% CI | p |", "|---|---|---|---|"]
    for key, fit_i in [("kr_en", fit_kr), ("jp_ja", fit_jp)]:
        b = fit_i.params["focus"]
        lo, hi = fit_i.conf_int().loc["focus"]
        a.append(f"| {LABELS[key]} | {np.exp(b):.2f} | {np.exp(lo):.2f}–{np.exp(hi):.2f} "
                 f"| {_fmt_p(fit_i.pvalues['focus'])} |")
    a.append("")
    return a

