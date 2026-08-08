"""生存分析の計算部品 (Phase 5)。

生存時間は**年単位の整数**である。結成年と解散年しか取れないため、
同一年に結成・解散したグループは duration = 0 になる。連続時間の手法を
そのまま当てると同順位 (tie) が大量に出るので、以下の方針で扱う:

- Kaplan-Meier / log-rank: 同順位をそのまま扱える。lifelines をそのまま使う
- ハザードの検証: **離散時間ハザード**として扱う。
  時点 t のリスク集合 = {duration >= t}、時点 t の死亡 = {duration == t かつ 死亡}
- Cox: 同順位は Efron 近似 (lifelines の既定) で扱う

★ 7 年地点のハザード集中が本研究の新規性の核心。韓国の標準専属契約は 7 年で、
  制度が生存曲線の形を作るなら t=7 に超過ハザードが出るはず。
  平滑な基準ハザードからの超過として、モデル非依存の検定とモデルベースの検定の
  両方で測る。
"""
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import multivariate_logrank_test, proportional_hazard_test
from scipy import stats

# 観測窓とコホート区切り (PLAN §観測窓の判断)
WINDOW_MAIN = (1996, 2025)
WINDOW_STABLE = (2009, 2025)   # 感度分析 A: 年 30 件以上を安定して確保できる区間
WINDOW_NOLAG = (1996, 2022)    # 感度分析 B: 直近 3 年の記事化ラグを除く

COHORT_BINS = [1995, 2000, 2005, 2010, 2015, 2020, 2025]
COHORT_LABELS = ["1996-2000", "2001-2005", "2006-2010",
                 "2011-2015", "2016-2020", "2021-2025"]

# 韓国の標準専属契約期間。ここでのハザード集中の有無が論文の焦点
CONTRACT_YEARS = 7


def to_cohort(formed_year):
    """デビュー年を 5 年区切りのコホートに割り当てる。"""
    return pd.cut(formed_year, bins=COHORT_BINS, labels=COHORT_LABELS)


# --- Kaplan-Meier ----------------------------------------------------------

def km_fit(durations, observed, label=None):
    return KaplanMeierFitter(label=label or "KM").fit(durations, observed)


def km_at(durations, observed, times):
    """指定時点の生存率と 95% 信頼区間を返す。

    lifelines の predict は打ち切りだけの時点も含めて階段関数を評価するので、
    `1 - S(t)` は「t 年目までに離脱した割合」になる。
    """
    kmf = km_fit(durations, observed)
    ci = kmf.confidence_interval_survival_function_
    rows = []
    for t in times:
        s = float(kmf.predict(t))
        # 信頼区間は階段関数なので t 以下で最後の行を採る
        idx = ci.index[ci.index <= t]
        lo, hi = (float(ci.loc[idx[-1]].iloc[0]), float(ci.loc[idx[-1]].iloc[1])) \
            if len(idx) else (np.nan, np.nan)
        rows.append({"t": t, "survival": s, "ci_low": lo, "ci_high": hi,
                     "exit": 1 - s, "n_risk": int((np.asarray(durations) >= t).sum())})
    return pd.DataFrame(rows)


def median_survival(durations, observed):
    """生存期間中央値。打ち切りが多く到達しない場合は NaN。"""
    kmf = km_fit(durations, observed)
    m = kmf.median_survival_time_
    return float(m) if np.isfinite(m) else np.nan


def logrank(df, group_col, duration_col, event_col):
    """群間の log-rank 検定 (2 群でも多群でも同じ関数で扱える)。"""
    res = multivariate_logrank_test(
        df[duration_col], df[group_col], df[event_col])
    return {"test_statistic": float(res.test_statistic),
            "p_value": float(res.p_value),
            "df": int(res.degrees_of_freedom)}


# --- 離散時間ハザード -------------------------------------------------------

def discrete_hazard(durations, observed, t_max=15):
    """各年の条件付きハザードを返す。

    h(t) = (t 年目に死亡した数) / (t 年目の開始時点でリスクに晒されている数)

    信頼区間は二項比率の Wilson 区間。年単位の粗いデータなので、
    連続時間の平滑化はかけずに素の値を出す。
    """
    d = np.asarray(durations, dtype=float)
    e = np.asarray(observed, dtype=bool)
    rows = []
    for t in range(0, t_max + 1):
        n = int((d >= t).sum())
        k = int(((d == t) & e).sum())
        if n == 0:
            continue
        lo, hi = _wilson(k, n)
        rows.append({"t": t, "n_risk": n, "deaths": k,
                     "hazard": k / n, "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


def _wilson(k, n, z=1.96):
    """二項比率の Wilson 信頼区間。"""
    if n == 0:
        return np.nan, np.nan
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def excess_hazard_test(durations, observed, focus=CONTRACT_YEARS,
                       neighbors=(5, 6, 8, 9)):
    """近傍年のハザードを基準に、focus 年の超過を二項検定で測る。

    モデル非依存で、何を比べているかが読者に見えるのが利点。
    基準ハザードを近傍から推定している分だけ検定はやや非保守的なので、
    モデルベースの検定 (cloglog) と併せて報告すること。
    """
    h = discrete_hazard(durations, observed, t_max=max(max(neighbors), focus))
    h = h.set_index("t")
    if focus not in h.index:
        return None
    nb = h.loc[[t for t in neighbors if t in h.index]]
    n_nb, k_nb = int(nb["n_risk"].sum()), int(nb["deaths"].sum())
    if n_nb == 0:
        return None
    h0 = k_nb / n_nb
    k, n = int(h.loc[focus, "deaths"]), int(h.loc[focus, "n_risk"])
    res = stats.binomtest(k, n, h0, alternative="greater")
    return {"focus": focus, "deaths": k, "n_risk": n,
            "hazard": k / n, "baseline_hazard": h0,
            "ratio": (k / n) / h0 if h0 > 0 else np.nan,
            "neighbors": list(neighbors), "p_value": float(res.pvalue)}


def person_period(df, duration_col, event_col, t_max=15, keep=()):
    """離散時間ハザードモデル用に、1 行 = 1 グループ × 1 年 に展開する。

    グループ i は t = 0..d_i の各年でリスクに晒され、死亡なら t = d_i で
    イベントが立つ。t_max より後ろは切り落とす (後半は risk set が薄く、
    平滑な基準ハザードの推定を不安定にするため)。
    """
    rows = []
    for _, r in df.iterrows():
        d = int(min(r[duration_col], t_max))
        died = bool(r[event_col]) and r[duration_col] <= t_max
        base = {k: r[k] for k in keep}
        for t in range(0, d + 1):
            rows.append({**base, "t": t, "event": int(died and t == d)})
    return pd.DataFrame(rows)


def cloglog_excess(pp, focus=CONTRACT_YEARS, degree=3, by=None):
    """離散時間ハザードモデルで focus 年の超過ハザードを検定する。

        cloglog(h(t)) = 多項式(t) + β·1{t = focus}

    基準ハザードを **平滑な多項式**に置くのが肝。t を因子にすると
    1{t = focus} と共線になって超過を定義できない。
    by を渡すと群ごとに基準ハザードと超過を別々に推定する
    (基準の形の違いを超過と取り違えないため)。

    cloglog リンクを使うのは、離散時間の比例ハザードモデルに対応し、
    係数がハザード比の対数として読めるため。
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    pp = pp.copy()
    pp["focus"] = (pp["t"] == focus).astype(int)
    poly = " + ".join(f"I(t**{k})" for k in range(1, degree + 1))
    if by:
        formula = f"event ~ ({poly}) * C({by}) + focus * C({by})"
    else:
        formula = f"event ~ {poly} + focus"
    model = smf.glm(formula, data=pp,
                    family=sm.families.Binomial(link=sm.families.links.CLogLog()))
    return model.fit()


# --- Cox 比例ハザード -------------------------------------------------------

def cox_fit(df, formula, duration_col="duration", event_col="event"):
    """Cox 比例ハザードモデル。同順位は Efron 近似 (lifelines 既定)。

    生存時間が年単位の整数で duration = 0 が存在するため、
    半年ずらして正の値にしてから当てる (区間 [t, t+1) の中点をとる慣行)。
    """
    d = df.copy()
    d[duration_col] = d[duration_col] + 0.5
    cph = CoxPHFitter()
    cph.fit(d, duration_col=duration_col, event_col=event_col, formula=formula)
    return cph, d


def schoenfeld(cph, df):
    """比例ハザード仮定の検定 (Schoenfeld 残差)。

    df は cox_fit が返した学習用データ (生存時間をずらした後のもの) を渡す。
    """
    return proportional_hazard_test(cph, df, time_transform="rank")
