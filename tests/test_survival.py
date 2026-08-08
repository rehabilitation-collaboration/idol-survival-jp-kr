"""生存データ (data/jp_survival.parquet) の整合性テスト。

死亡定義の包含関係と生存時間の妥当性を固定する。
定義を触ったときに、意図せず主分析の死亡率が動いたら気づけるようにする。
"""
import os

import pandas as pd
import pytest

PARQUET = os.path.join(os.path.dirname(__file__), "..", "data", "jp_survival.parquet")

pytestmark = pytest.mark.skipif(
    not os.path.exists(PARQUET),
    reason="生存データ未生成 (scripts/build_jp_survival.py)",
)

DEFS = ["conservative", "strict", "loose"]


@pytest.fixture(scope="module")
def sv():
    return pd.read_parquet(PARQUET)


def test_主キーが一意(sv):
    assert sv["group_id"].duplicated().sum() == 0


def test_死亡定義は包含関係にある(sv):
    # 保守 ⊆ 厳格 ⊆ 緩和。この順序が崩れたら定義のどれかが壊れている
    assert not (sv["death_conservative"] & ~sv["death_strict"]).any()
    assert not (sv["death_strict"] & ~sv["death_loose"]).any()


@pytest.mark.parametrize("name", DEFS)
def test_生存時間が負にならない(sv, name):
    assert (sv[f"duration_{name}"] >= 0).all()


@pytest.mark.parametrize("name", DEFS)
def test_死亡フラグと観測フラグが一致(sv, name):
    assert (sv[f"death_{name}"] == sv[f"observed_{name}"]).all()


@pytest.mark.parametrize("name", DEFS)
def test_死亡には死亡年があり打ち切りには無い(sv, name):
    dead = sv[sv[f"death_{name}"]]
    alive = sv[~sv[f"death_{name}"]]
    assert dead[f"year_{name}"].notna().all()
    assert alive[f"year_{name}"].isna().all()


@pytest.mark.parametrize("name", DEFS)
def test_死亡年は結成年以降(sv, name):
    d = sv[sv[f"death_{name}"]]
    assert (d[f"year_{name}"] >= d["cat_formed_year"]).all()


def test_打ち切りの生存時間は打ち切り年からの経過(sv):
    alive = sv[~sv["death_strict"]]
    assert (alive["duration_strict"] == 2026 - alive["cat_formed_year"]).all()


def test_二重ソースのどちらか一方だけが死亡を捉える例が存在する(sv):
    """厳格定義で 2 ソースを併用する根拠を固定する。

    片方に寄せると死亡を取りこぼすことを、データそのもので示す。
    """
    cat_only = sv["cat_dissolved_year"].notna() & sv["ib_end_year"].isna()
    ib_only = sv["cat_dissolved_year"].isna() & sv["ib_end_year"].notna()
    assert cat_only.sum() > 0, "解散カテゴリのみが捉える死亡が無い"
    assert ib_only.sum() > 0, "Infobox のみが捉える死亡が無い"
    # Infobox 側の上乗せが大きいことが、カテゴリ単独を主分析にしない理由
    assert ib_only.sum() > cat_only.sum()


def test_厳格定義は保守定義より死亡を多く捉える(sv):
    assert sv["death_strict"].sum() > sv["death_conservative"].sum()


def test_結成年の二ソース一致率が高い(sv):
    both = sv[sv["ib_start_year"].notna()]
    agree = (both["cat_formed_year"] == both["ib_start_year"]).mean()
    assert agree > 0.90, f"結成年の一致率が {agree:.1%} に低下している"
