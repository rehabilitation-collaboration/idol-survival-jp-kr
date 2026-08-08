"""Phase 5 の分析関数のテスト。

生存時間が年単位の整数で同順位が大量に出るデータなので、
手計算できる小さな例で挙動を固定しておく。
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import survival_analysis as sa  # noqa: E402


class TestDiscreteHazard:
    def test_手計算と一致する(self):
        # 5 組。duration/event = (1,死) (1,打) (2,死) (3,死) (5,打)
        d = [1, 1, 2, 3, 5]
        e = [True, False, True, True, False]
        h = sa.discrete_hazard(d, e, t_max=5).set_index("t")
        # t=0: リスク 5・死亡 0
        assert h.loc[0, "n_risk"] == 5 and h.loc[0, "deaths"] == 0
        # t=1: リスク 5 (duration>=1 が 5 組)・死亡 1
        assert h.loc[1, "n_risk"] == 5 and h.loc[1, "deaths"] == 1
        assert h.loc[1, "hazard"] == pytest.approx(1 / 5)
        # t=2: 打ち切りの 1 組が抜けてリスク 3
        assert h.loc[2, "n_risk"] == 3 and h.loc[2, "deaths"] == 1
        assert h.loc[3, "n_risk"] == 2 and h.loc[3, "deaths"] == 1
        # t=4 は死亡ゼロだがリスクは残る
        assert h.loc[4, "n_risk"] == 1 and h.loc[4, "deaths"] == 0

    def test_リスク集合が空の年は行を作らない(self):
        h = sa.discrete_hazard([1, 2], [True, True], t_max=10)
        assert h["t"].max() == 2

    def test_信頼区間がハザードを挟む(self):
        h = sa.discrete_hazard([3] * 20 + [5] * 20, [True] * 20 + [False] * 20, t_max=5)
        for _, r in h[h["deaths"] > 0].iterrows():
            assert r["ci_low"] <= r["hazard"] <= r["ci_high"]


class TestKM:
    def test_打ち切りがなければ経験分布と一致する(self):
        d = [1, 2, 3, 4, 5]
        t = sa.km_at(d, [True] * 5, [1, 3, 5])
        assert t.iloc[0]["survival"] == pytest.approx(0.8)
        assert t.iloc[1]["survival"] == pytest.approx(0.4)
        assert t.iloc[2]["survival"] == pytest.approx(0.0)

    def test_離脱率は1から生存率を引いた値(self):
        t = sa.km_at([1, 2, 3], [True, True, False], [2])
        assert t.iloc[0]["exit"] == pytest.approx(1 - t.iloc[0]["survival"])

    def test_Phase3の素朴な実装と一致する(self):
        """`scripts/build_en_population.py` の km_survival と同じ値になること。

        Phase 3 で公表済みの数値 (3 年離脱率 20.1% 等) が
        lifelines への載せ替えで動いていないことを担保する。
        """
        rng = np.random.default_rng(0)
        d = rng.integers(0, 20, 300).astype(float)
        e = rng.random(300) < 0.4

        def naive(durations, observed, t):
            df = pd.DataFrame({"d": durations, "e": observed}).sort_values("d")
            s, n = 1.0, len(df)
            for dd, grp in df.groupby("d"):
                if dd > t:
                    break
                deaths = int(grp["e"].sum())
                if n > 0 and deaths:
                    s *= 1 - deaths / n
                n -= len(grp)
            return s

        for t in [1, 3, 5, 7, 10]:
            assert sa.km_at(d, e, [t]).iloc[0]["survival"] == pytest.approx(naive(d, e, t))


class TestExcessHazard:
    def test_超過がなければ比が1前後で有意にならない(self):
        # 全年で一定ハザードになるようなデータを組む
        rng = np.random.default_rng(1)
        d, e = [], []
        for _ in range(2000):
            t = 0
            while t < 15 and rng.random() > 0.1:
                t += 1
            d.append(t)
            e.append(t < 15)
        r = sa.excess_hazard_test(d, e)
        assert 0.7 < r["ratio"] < 1.4
        assert r["p_value"] > 0.05

    def test_7年に山を仕込むと検出できる(self):
        # t=7 のリスク集合に死亡を厚く積む
        d = [7] * 60 + [5] * 30 + [6] * 30 + [8] * 30 + [9] * 30 + [15] * 200
        e = [True] * 180 + [False] * 200
        r = sa.excess_hazard_test(d, e)
        assert r["ratio"] > 1.5
        assert r["p_value"] < 0.01

    def test_近傍を変えても結果が返る(self):
        d = [7] * 20 + [6] * 20 + [8] * 20 + [15] * 50
        e = [True] * 60 + [False] * 50
        assert sa.excess_hazard_test(d, e, neighbors=(6, 8)) is not None

    def test_対象年にリスクがなければNone(self):
        assert sa.excess_hazard_test([1, 2], [True, True], focus=7) is None


class TestPersonPeriod:
    def test_行数はduration合計プラス人数(self):
        df = pd.DataFrame({"duration": [0.0, 2.0, 3.0], "event": [1, 1, 0]})
        pp = sa.person_period(df, "duration", "event")
        assert len(pp) == (0 + 1) + (2 + 1) + (3 + 1)

    def test_イベントは最終年にだけ立つ(self):
        df = pd.DataFrame({"duration": [3.0], "event": [1]})
        pp = sa.person_period(df, "duration", "event")
        assert pp["event"].tolist() == [0, 0, 0, 1]

    def test_打ち切りはイベントが立たない(self):
        df = pd.DataFrame({"duration": [3.0], "event": [0]})
        assert sa.person_period(df, "duration", "event")["event"].sum() == 0

    def test_tmaxを超える死亡は打ち切り扱いになる(self):
        df = pd.DataFrame({"duration": [20.0], "event": [1]})
        pp = sa.person_period(df, "duration", "event", t_max=15)
        assert len(pp) == 16 and pp["event"].sum() == 0

    def test_keepで列を持ち越せる(self):
        df = pd.DataFrame({"duration": [2.0], "event": [1], "country": ["KR"]})
        pp = sa.person_period(df, "duration", "event", keep=("country",))
        assert (pp["country"] == "KR").all()


class TestCloglog:
    def test_仕込んだ超過を検出できる(self):
        rng = np.random.default_rng(2)
        rows = []
        for _ in range(3000):
            t = 0
            while t < 15:
                h = 0.30 if t == 7 else 0.06
                if rng.random() < h:
                    break
                t += 1
            rows.append({"duration": float(t), "event": int(t < 15)})
        pp = sa.person_period(pd.DataFrame(rows), "duration", "event")
        fit = sa.cloglog_excess(pp)
        assert np.exp(fit.params["focus"]) > 2.0
        assert fit.pvalues["focus"] < 0.001

    def test_超過がなければ有意にならない(self):
        rng = np.random.default_rng(3)
        rows = []
        for _ in range(3000):
            t = 0
            while t < 15 and rng.random() > 0.08:
                t += 1
            rows.append({"duration": float(t), "event": int(t < 15)})
        pp = sa.person_period(pd.DataFrame(rows), "duration", "event")
        fit = sa.cloglog_excess(pp)
        assert fit.pvalues["focus"] > 0.05


class TestCohortAndCox:
    def test_コホートの割り当て(self):
        s = sa.to_cohort(pd.Series([1996, 2000, 2001, 2025]))
        assert list(s.astype(str)) == ["1996-2000", "1996-2000", "2001-2005", "2021-2025"]

    def test_Coxはゼロ生存時間をずらして当てる(self):
        rng = np.random.default_rng(4)
        n = 400
        x = rng.integers(0, 2, n)
        d = pd.DataFrame({
            "duration": rng.integers(0, 10, n).astype(float),
            "event": (rng.random(n) < 0.5).astype(int),
            "grp": np.where(x == 1, "a", "b"),
        })
        cph, fit_df = sa.cox_fit(d, "grp")
        assert (fit_df["duration"] > 0).all()
        assert len(cph.summary) == 1

    def test_完全に同じ2群はlogrankで有意にならない(self):
        # 乱数の引き当てに依存しないよう、2 群に同一のデータを与える
        rng = np.random.default_rng(5)
        n = 300
        base = pd.DataFrame({
            "duration": rng.integers(0, 12, n).astype(float),
            "event": (rng.random(n) < 0.5).astype(int),
        })
        df = pd.concat([base.assign(g="x"), base.assign(g="y")], ignore_index=True)
        r = sa.logrank(df, "g", "duration", "event")
        assert r["p_value"] == pytest.approx(1.0)
        assert r["df"] == 1

    def test_明らかに違う2群はlogrankで有意になる(self):
        n = 200
        df = pd.concat([
            pd.DataFrame({"duration": [1.0] * n, "event": 1, "g": "short"}),
            pd.DataFrame({"duration": [12.0] * n, "event": 1, "g": "long"}),
        ], ignore_index=True)
        assert sa.logrank(df, "g", "duration", "event")["p_value"] < 0.001
