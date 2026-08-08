"""事務所抽出のテスト (Cox の共変量「事務所規模」の入力)。

ケースは全て `data/raw/ja_pages.jsonl` の実値から採っている。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agency import extract_agencies, normalize_agency, primary_agency  # noqa: E402


class TestNormalize:
    def test_年の範囲を落とす(self):
        assert normalize_agency("スターダストプロモーション（2018年 - 2026年）") == "スターダストプロモーション"

    def test_法人格を落とす(self):
        assert normalize_agency("株式会社LIVE PLANET") == "LIVE PLANET"
        assert normalize_agency("バズウェーブ合同会社") == "バズウェーブ"

    def test_国名ラベルを落とす(self):
        assert normalize_agency("韓国：Illusion") == "Illusion"

    def test_末尾のなどを落とす(self):
        assert normalize_agency("プロダクション尾木など") == "プロダクション尾木"

    def test_無所属は欠損ではなく無所属として残る(self):
        # 接尾辞「所属」を先に落とすと「無」になって捨てられる
        assert normalize_agency("無所属（セルフプロデュース）") == "無所属"
        assert normalize_agency("無所属(セルフプロデュース)") == "無所属"
        assert normalize_agency("フリーランス") == "無所属"

    def test_長音符を末尾から削らない(self):
        # 「ー」(U+30FC) を strip 対象に入れると同じ事務所が 2 つに割れる
        assert normalize_agency("アップフロントエージェンシー") == "アップフロントエージェンシー"
        assert normalize_agency("エコーズエンタテイメント") == "エコーズエンタテイメント"

    def test_見た目の似たダッシュは削る(self):
        assert normalize_agency("ホリプロ-") == "ホリプロ"

    def test_意味のない値はNone(self):
        assert normalize_agency("") is None
        assert normalize_agency("不明") is None
        assert normalize_agency("-") is None
        assert normalize_agency("各メンバーの所属は所属事務所およびメンバーを参照") is None

    def test_改称と表記ゆれを寄せる(self):
        assert normalize_agency("SMILE-UP.") == "ジャニーズ事務所"
        assert normalize_agency("STARTO ENTERTAINMENT") == "ジャニーズ事務所"
        assert normalize_agency("エイベックス・マネジメント") == "エイベックス"
        assert normalize_agency("ASOBISYSTEM") == "アソビシステム"


class TestExtract:
    def test_改称の連鎖は先頭が結成時の事務所(self):
        raw = "ジャニーズ事務所→SMILE-UP.（1995年 - 2024年）\nSTARTO ENTERTAINMENT（2024年 - ）"
        assert primary_agency(raw) == "ジャニーズ事務所"
        # 寄せた結果として重複は畳まれる
        assert extract_agencies(raw) == ["ジャニーズ事務所"]

    def test_箇条書きタグで区切る(self):
        raw = "<ol><li>ジャニーズ事務所<li>SMILE-UP. (2015年 - 2024年)<li>STARTO ENTERTAINMENT</ol>"
        assert primary_agency(raw) == "ジャニーズ事務所"

    def test_改行で複数の事務所を取る(self):
        raw = "ホリプロ \n太田プロダクション \nボックスコーポレーション"
        assert extract_agencies(raw) == ["ホリプロ", "太田プロダクション", "ボックスコーポレーション"]

    def test_Plainlistテンプレートを剥がす(self):
        # 修正前は '{{Plainlist|' が事務所名として 48 件計上されていた
        raw = "{{Plainlist|\n* [[スターダストプロモーション]]\n* [[エイトワン]]\n}}"
        assert extract_agencies(raw) == ["スターダストプロモーション", "エイトワン"]

    def test_外部リンクは表示名を残す(self):
        raw = "[https://example.com/ ワタナベエンターテインメント]"
        assert primary_agency(raw) == "ワタナベエンターテインメント"

    def test_表示名のない外部リンクは捨てる(self):
        assert primary_agency("[https://example.com/]") is None

    def test_HTMLコメントだけの値は欠損(self):
        assert primary_agency("<!--[[ギルドロップス#メンバー|下記参照]]-->") is None

    def test_smallタグ付きの年範囲(self):
        raw = "Whole World Media<small>（2020年 - 2021年）</small>\nVINEYARD<small>（2021年 - 現在）</small>"
        assert extract_agencies(raw) == ["Whole World Media", "VINEYARD"]

    def test_国別表記の併記(self):
        assert extract_agencies("韓国：Illusion\n日本：株式会社伝元") == ["Illusion", "伝元"]

    def test_空とNone(self):
        assert extract_agencies(None) == []
        assert extract_agencies("") == []
        assert primary_agency(None) is None


@pytest.mark.parametrize("raw,expected", [
    ("YX LABELS", "YX LABELS"),
    ("エイベックス・エンタテインメント（2005年 - 2009年）\nエイベックス・マネジメント（2009年 - ）", "エイベックス"),
    ("[[スターダストプロモーション]]", "スターダストプロモーション"),
    ("株式会社L&L’s（2019年 - ） ", "L&L’s"),
])
def test_実値サンプル(raw, expected):
    assert primary_agency(raw) == expected
