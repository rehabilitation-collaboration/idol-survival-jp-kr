"""確定した母集団 (data/jp_groups.parquet) の整合性テスト。

生成物そのものを検証する。母集団はプロジェクトの全ての数字の土台なので、
再取得や判定ルールの変更で壊れたら気づけるようにしておく。

母集団の生成には Wikipedia からの取得 (約 35 分) が要るため、
parquet が無い環境ではスキップする。
"""
import os
import re

import pandas as pd
import pytest

PARQUET = os.path.join(os.path.dirname(__file__), "..", "data", "jp_groups.parquet")

pytestmark = pytest.mark.skipif(
    not os.path.exists(PARQUET),
    reason="母集団未生成 (scripts/fetch_jp_population.py -> build_jp_population.py)",
)


@pytest.fixture(scope="module")
def pop():
    return pd.read_parquet(PARQUET)


def test_主キーが一意(pop):
    assert pop["group_id"].duplicated().sum() == 0


def test_母集団が空でない(pop):
    # 判定ルールが壊れると 0 件や全件になる。桁が変わったら気づけるようにする
    assert 500 < len(pop) < 3000


def test_結成年が観測窓に収まる(pop):
    assert pop["formed_year"].between(1996, 2025).all()


def test_解散年は結成年以降(pop):
    d = pop.dropna(subset=["dissolved_year"])
    assert (d["dissolved_year"] >= d["formed_year"]).all()


def test_打ち切りフラグと解散年が整合する(pop):
    assert (pop["is_censored"] == pop["dissolved_year"].isna()).all()


def test_全件が判定シグナルのいずれかで陽性(pop):
    signal = pop["c1_category"] | pop["c2_lead_idol"] | pop["c3_dance_vocal"]
    assert signal.all()


def test_厳格定義は主定義の部分集合(pop):
    assert not (pop["is_idol_strict"] & ~pop["is_idol"]).any()


def test_外国のグループが混入していない(pop):
    # 日本への言及がないまま外国名だけを持つ記事は除外されているはず
    foreign = pop["lead_sentence"].str.contains(
        r"韓国|大韓民国|K-POP|中華人民共和国|台湾|アメリカ|イギリス", regex=True, na=False
    )
    jp = pop["lead_sentence"].str.contains(r"日本|邦楽", regex=True, na=False)
    leaked = pop[foreign & ~jp]
    assert leaked.empty, f"外国グループが {len(leaked)} 件残っている: {leaked['name'].tolist()[:5]}"


def test_性別が想定の値のみ(pop):
    assert set(pop["sex"]) <= {"F", "M", "mixed", "unknown"}


def test_判定シグナル文字列が実フラグと一致する(pop):
    for _, r in pop.head(200).iterrows():
        expected = "+".join(
            k for k, v in [
                ("C1", r["c1_category"]), ("C2", r["c2_lead_idol"]), ("C3", r["c3_dance_vocal"])
            ] if v
        )
        assert r["idol_signal"] == expected


def test_直近年の結成数が減少している(pop):
    """記事化ラグの存在を明示的に固定する。

    実態ではなく Wikipedia の記事作成が追いついていないことによる減少。
    これが消えたら観測窓の判断をやり直す必要がある。
    """
    recent = pop[pop["formed_year"].between(2023, 2025)].groupby("formed_year").size()
    peak = pop[pop["formed_year"].between(2018, 2022)].groupby("formed_year").size()
    assert recent.min() < peak.max(), "直近年の落ち込みが消えている。観測窓の判断を再検討すること"
