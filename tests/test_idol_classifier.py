"""アイドル判定ルールのテスト。

冒頭定義文は 2026-08-08 に ja.wikipedia API から実取得したものを使う
(action=query&prop=extracts&exintro=1&explaintext=1)。
判定の分岐を作った実例をそのまま固定して、リグレッションを検出する。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from idol_classifier import classify, first_sentence  # noqa: E402

# --- 実取得した冒頭テキスト (2026-08-08) ---
LEAD_SMAP = (
    "SMAP（スマップ）は、日本の男性アイドルグループ。1988年に結成し、1991年に"
    "『Can't Stop!! -LOVING-』でCDデビュー。2016年12月31日に解散した。"
)
LEAD_MOMUSU = (
    "モーニング娘。（モーニングむすめ）は、ハロー!プロジェクトに所属する"
    "日本の女性アイドルグループ。所属事務所はアップフロントプロモーション。"
)
LEAD_EXILE = (
    "EXILE（エグザイル）は、日本のダンス&ボーカルグループ。"
    "所属事務所はLDH JAPAN。レーベルはrhythm zone。"
)
LEAD_TWICE = (
    "TWICE（トゥワイス、朝: 트와이스）は、韓国の9人組ガールズグループ。"
    "JYPエンターテインメント所属。"
)


class TestFirstSentence:
    def test_記事名に句点を含んでも述部が取れる(self):
        # 素朴に最初の句点で切ると「モーニング娘。」だけになり判定が全滅する
        s = first_sentence(LEAD_MOMUSU)
        assert "アイドルグループ" in s

    def test_定義文の後ろの文は含めない(self):
        s = first_sentence(LEAD_SMAP)
        assert "解散" not in s

    def test_空文字を渡しても落ちない(self):
        assert first_sentence("") == ""
        assert first_sentence(None) == ""


class TestClassify:
    def test_カテゴリになくても冒頭定義文でアイドル判定できる(self):
        # 旧ジャニーズ系はアイドル系カテゴリに一切入っていない (実測)
        r = classify([], LEAD_SMAP)
        assert r["c1_category"] is False
        assert r["c2_lead_idol"] is True
        assert r["is_idol"] is True
        assert r["sex"] == "M"

    def test_ダンスボーカル系は主分析に入り厳格定義から外れる(self):
        r = classify([], LEAD_EXILE)
        assert r["c2_lead_idol"] is False
        assert r["c3_dance_vocal"] is True
        assert r["is_idol"] is True
        assert r["is_idol_strict"] is False

    def test_韓国グループは日本の母集団から除外される(self):
        r = classify([], LEAD_TWICE)
        assert r["is_foreign"] is True
        assert r["is_idol"] is False

    def test_冒頭がアイドルでも韓国なら除外される(self):
        # 2PM の冒頭定義文の形。「アイドル」と「韓国」が同居する
        r = classify([], "2PMは、韓国の6人組男性アイドルグループ。")
        assert r["c2_lead_idol"] is True
        assert r["is_idol"] is False

    @pytest.mark.parametrize(
        "lead",
        [
            # ja.wikipedia の年別カテゴリは全世界対象なので、韓国以外の外国も混入する
            "SNH48は、中華人民共和国・上海市を中心に活動する女性アイドルグループ。",
            "S.H.Eは、台湾のアイドルユニット。",
            "アトミック・キトゥンは、イギリスのリバプールで結成されたアイドルグループ。",
            "Jump5は、アメリカのアイドル・ダンスグループである。",
        ],
    )
    def test_韓国以外の外国グループも除外される(self, lead):
        r = classify([], lead)
        assert r["is_foreign"] is True
        assert r["is_idol"] is False

    def test_日本と外国の両方に言及があれば残す(self):
        # 日韓両拠点のグループ。実測で 4 件あり、境界事例として主分析に含める
        r = classify([], "AWEEKは、2018年に結成した日本・韓国両国で活動する7人組の男性アイドルグループ。")
        assert r["is_foreign"] is False
        assert r["is_multinational"] is True
        assert r["is_idol"] is True
        assert r["definition_sensitive"] is True

    def test_ダンスボーカルのみで拾った場合は定義感応と印付けされる(self):
        r = classify([], LEAD_EXILE)
        assert r["definition_sensitive"] is True

    def test_カテゴリと冒頭の両方で陽性なら定義感応ではない(self):
        r = classify(["日本の女性アイドルグループ"], LEAD_MOMUSU)
        assert r["definition_sensitive"] is False

    def test_カテゴリのみ陽性なら不一致フラグが立つ(self):
        r = classify(["日本の女性アイドルグループ"], "○○は、日本の音楽ユニット。")
        assert r["c1_category"] is True
        assert r["c2_lead_idol"] is False
        assert r["signal_disagree"] is True
        assert r["is_idol"] is True

    def test_両方陽性なら不一致フラグは立たない(self):
        r = classify(["日本の女性アイドルグループ"], LEAD_MOMUSU)
        assert r["signal_disagree"] is False

    def test_アイドルでない音楽グループは陰性(self):
        r = classify([], "いきものがかりは、日本の2人組音楽グループ。")
        assert r["is_idol"] is False


class TestYearExtraction:
    def test_結成年と解散年をカテゴリから取る(self):
        r = classify(
            ["2005年に結成した音楽グループ", "2016年に解散した音楽グループ"], LEAD_SMAP
        )
        assert r["formed_year_cat"] == 2005
        assert r["dissolved_year_cat"] == 2016

    def test_解散カテゴリがなければNone(self):
        r = classify(["2005年に結成した音楽グループ"], LEAD_SMAP)
        assert r["dissolved_year_cat"] is None

    def test_年カテゴリが複数あれば最も早い年を採る(self):
        # 再結成で複数の結成年カテゴリを持つ記事がある
        r = classify(
            ["1997年に結成した音楽グループ", "2014年に結成した音楽グループ"], LEAD_MOMUSU
        )
        assert r["formed_year_cat"] == 1997


class TestSex:
    @pytest.mark.parametrize(
        "categories,lead,expected",
        [
            (["日本の女性アイドルグループ"], "", "F"),
            (["日本の男性アイドルグループ"], "", "M"),
            ([], "○○は、日本の男女混合パフォーマンスグループ。", "mixed"),
            ([], "○○は、日本の女性アイドルグループ。", "F"),
            ([], "○○は、日本の音楽グループ。", "unknown"),
        ],
    )
    def test_性別判定(self, categories, lead, expected):
        assert classify(categories, lead)["sex"] == expected
