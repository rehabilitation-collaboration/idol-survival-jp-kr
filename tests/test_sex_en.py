"""英語版 Wikipedia からの性別導出のテスト。

ケースは `data/raw/en_{kr,jp}_pages.jsonl` の実値から採っている。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from sex_en import infer_sex_en, sex_from_categories, sex_from_lead  # noqa: E402


class TestCategories:
    def test_基本(self):
        assert sex_from_categories(["South Korean boy bands", "K-pop music groups"]) == "M"
        assert sex_from_categories(["Japanese girl groups"]) == "F"
        assert sex_from_categories(["South Korean co-ed groups"]) == "mixed"

    def test_同名カテゴリを拾わない(self):
        # 記事自身のカテゴリ。単数 + 括弧なので接尾辞一致しない
        assert sex_from_categories(["April (girl group)"]) is None
        assert sex_from_categories(["Rainbow (girl group)", "Girl's Day"]) is None

    def test_無関係なカテゴリを拾わない(self):
        assert sex_from_categories(["Magical girl anime and manga"]) is None
        assert sex_from_categories(["Lists of South Korean women"]) is None
        assert sex_from_categories(["Women in World War II"]) is None

    def test_混成カテゴリが優先される(self):
        assert sex_from_categories(
            ["Japanese girl groups", "Japanese co-ed groups"]) == "mixed"

    def test_男女のカテゴリが両方付いたら断定しない(self):
        assert sex_from_categories(
            ["South Korean boy bands", "South Korean girl groups"]) is None

    def test_デュオトリオ表記(self):
        assert sex_from_categories(["Female musical duos"]) == "F"
        assert sex_from_categories(["South Korean male musical duos"]) == "M"
        assert sex_from_categories(["Male–female musical duos"]) == "mixed"

    def test_空(self):
        assert sex_from_categories([]) is None
        assert sex_from_categories(None) is None


class TestLead:
    def test_基本(self):
        assert sex_from_lead("100% was a South Korean boy band formed by TOP Media.") == "M"
        assert sex_from_lead("Stellar was a South Korean girl group.") == "F"

    def test_混成表記(self):
        assert sex_from_lead("ZOCX is a Japanese alternative idol co-ed group.") == "mixed"
        assert sex_from_lead("KARD is a South Korean mixed-gender group.") == "mixed"

    def test_性別が書かれていない(self):
        assert sex_from_lead("15& was a South Korean duo formed by JYP Entertainment.") is None
        assert sex_from_lead("Buzz is a South Korean pop rock band formed in 2000.") is None

    def test_男女が併記されたら断定しない(self):
        lead = ("Fudanjuku is a sub-group of the Japanese idol girl group "
                "Nakano Fujo Sisters. Fudanjuku is its alter-ego boy band.")
        assert sex_from_lead(lead) is None

    def test_女性グループの別表記(self):
        assert sex_from_lead("They are an all-female band from Tokyo.") == "F"
        assert sex_from_lead("Sweet Sorrow is a South Korean male vocal group.") == "M"


class TestInfer:
    def test_カテゴリが優先される(self):
        # カテゴリの方が付与率が高い (韓国 89.4% / 日本 86.7%)
        sex, src = infer_sex_en(["South Korean girl groups"], "was a South Korean group.")
        assert (sex, src) == ("F", "category")

    def test_カテゴリが無ければリード文に落とす(self):
        sex, src = infer_sex_en(["K-pop music groups"], "is a South Korean boy band.")
        assert (sex, src) == ("M", "lead")

    def test_どちらも取れなければ不明(self):
        sex, src = infer_sex_en(["K-pop music groups"], "is a South Korean duo.")
        assert (sex, src) == ("unknown", "none")

    def test_カテゴリが衝突したらリード文に譲る(self):
        sex, src = infer_sex_en(
            ["South Korean boy bands", "South Korean girl groups"],
            "is a South Korean girl group.")
        assert (sex, src) == ("F", "lead")
