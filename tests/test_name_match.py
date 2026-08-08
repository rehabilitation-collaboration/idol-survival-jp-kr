"""グループ名の名寄せのテスト。

RIAJ 認定のアーティスト名と Wikipedia の記事タイトルを突き合わせる。
正規化を強めすぎると別グループが衝突するので、その境界を固定する。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from name_match import build_index, normalize  # noqa: E402


class TestNormalize:
    def test_曖昧回避の括弧を落とす(self):
        assert normalize("嵐 (グループ)") == normalize("嵐")
        assert normalize("V6 (グループ)") == normalize("V6")

    def test_全角半角を吸収する(self):
        assert normalize("ＡＫＢ４８") == normalize("AKB48")

    def test_大文字小文字を吸収する(self):
        assert normalize("Perfume") == normalize("PERFUME")

    def test_中黒とスペースを無視する(self):
        assert normalize("安室 奈美恵") == normalize("安室奈美恵")
        assert normalize("Kis-My-Ft2") == normalize("KisMyFt2")

    def test_グループ名の句点は残す(self):
        # 「モーニング娘。」の句点は名前の一部
        assert normalize("モーニング娘。") != normalize("モーニング娘")

    def test_長音符は残す(self):
        assert normalize("ベビーメタル") != normalize("ベビメタル")

    def test_空やNoneでも落ちない(self):
        assert normalize("") == ""
        assert normalize(None) == ""

    def test_別グループが衝突しない(self):
        # 正規化を強めすぎると別物が同一視される。ここが崩れたら過剰正規化
        assert normalize("w-inds.") != normalize("Winds")
        assert normalize("E-girls") != normalize("Egirl")


class TestBuildIndex:
    def test_同じキーの名前をまとめる(self):
        idx = build_index(["嵐 (グループ)", "嵐"])
        assert len(idx) == 1
        assert len(next(iter(idx.values()))) == 2

    def test_別名は別キーになる(self):
        idx = build_index(["AKB48", "SKE48"])
        assert len(idx) == 2


@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(os.path.dirname(__file__), "..", "data", "jp_certifications.parquet")
    ),
    reason="認定データ未生成 (scripts/build_hit_data.py)",
)
class TestCertificationData:
    @pytest.fixture(scope="class")
    def cert(self):
        import pandas as pd
        return pd.read_parquet(
            os.path.join(os.path.dirname(__file__), "..", "data", "jp_certifications.parquet")
        )

    def test_母集団と同じ件数(self, cert):
        assert len(cert) == 1346

    def test_認定ありは認定数が正(self, cert):
        c = cert[cert["has_certification"]]
        assert (c["n_certifications"] > 0).all()
        assert len(c) > 0

    def test_認定なしは認定数がゼロ(self, cert):
        c = cert[~cert["has_certification"]]
        assert (c["n_certifications"] == 0).all()

    def test_主要グループが認定ありと判定される(self, cert):
        # 名寄せが壊れたら気づけるようにする。
        # 観測窓 1996-2025 の内側にあるグループだけを使う
        # (SMAP は 1988 年結成で窓の外なので母集団に入らない)
        for name in ["嵐 (グループ)", "AKB48", "モーニング娘。", "EXILE"]:
            row = cert[cert["name"] == name]
            assert len(row) == 1, f"{name} が母集団に無い"
            assert bool(row.iloc[0]["has_certification"]), f"{name} の認定が紐づいていない"

    def test_観測窓より前に結成したグループは母集団に入らない(self, cert):
        # Kim (2026) に揃えた 1996-2025 の窓。SMAP (1988) や
        # 光GENJI (1987) は対象外になる
        assert cert["formed_year"].min() >= 1996
        assert "SMAP" not in set(cert["name"])
