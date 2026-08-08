"""en.wikipedia 版の判定ロジックのテスト。

冒頭定義文は 2026-08-08 に en.wikipedia API から実取得したものを使う。
英語のピリオドは略語にも使われるので、文の切り方が壊れると
主要グループごと判定から落ちる。そこを回帰テストで固定する。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from en_classifier import (  # noqa: E402
    classify_en,
    detect_disband_year,
    first_sentence,
    parse_years_active_en,
)

# --- 実取得した冒頭テキスト (2026-08-08) ---
LEAD_BTS = (
    "BTS (Korean: 방탄소년단; RR: Bangtan sonyeondan; lit. 'Bulletproof Boy Scouts'), "
    "also known as the Bangtan Boys, is a South Korean boy band formed in 2010."
)
LEAD_TWICE = "Twice (Korean: 트와이스) is a South Korean girl group formed by JYP Entertainment."
LEAD_BAP = (
    "B.A.P (Korean: 비에이피; an acronym for Best Absolute Perfect), was a South Korean "
    "boy band formed by TS Entertainment in 2012. The group disbanded in 2019."
)
LEAD_100 = (
    "100% (Korean: 백퍼센트) was a South Korean boy band formed by Shinhwa's Andy Lee "
    "under TOP Media in 2012."
)


class TestFirstSentence:
    def test_略語のピリオドで文を切らない(self):
        # ★ 最初の '.' で切ると "lit." で終わり、主節に届かず BTS が判定不能になる
        s = first_sentence(LEAD_BTS)
        assert "boy band" in s

    def test_本当の文末では切る(self):
        s = first_sentence(LEAD_BAP)
        assert "disbanded" not in s

    def test_空文字でも落ちない(self):
        assert first_sentence("") == ""
        assert first_sentence(None) == ""


class TestClassifyEn:
    def test_現在形は現存として扱う(self):
        r = classify_en(["Musical groups established in 2010"], LEAD_BTS, "2010–present")
        assert r["is_past_tense"] is False
        assert r["death_year"] is None
        assert "boy band" in r["kinds"]

    def test_過去形とリード文から解散年を取る(self):
        r = classify_en(["Musical groups established in 2012"], LEAD_BAP, None)
        assert r["is_past_tense"] is True
        assert r["death_year"] == 2019
        assert r["death_without_year"] is False

    def test_解散カテゴリを最優先する(self):
        r = classify_en(
            ["Musical groups established in 2012", "Musical groups disestablished in 2021"],
            LEAD_100, "2012–2021",
        )
        assert r["cat_formed_year"] == 2012
        assert r["death_year"] == 2021

    def test_過去形だが年が取れない場合は印を付ける(self):
        r = classify_en(["Musical groups established in 2017"], LEAD_100, None)
        assert r["is_past_tense"] is True
        assert r["death_year"] is None
        assert r["death_without_year"] is True

    def test_ロックバンドは非アイドルとして扱う(self):
        r = classify_en([], "X is a South Korean rock band formed in 2010.", None)
        assert r["is_idol"] is False

    def test_バンド表記でもガールグループなら残す(self):
        lead = "X is a South Korean girl group and rock band formed in 2010."
        assert classify_en([], lead, None)["is_idol"] is True

    def test_種別は第1文の外にあっても拾う(self):
        # 'B.O.Y' のように略語で文が切れる記事があるため、種別は冒頭全体を見る
        lead = "B.O.Y (Korean: 비오브유; acronym of and pronounced as B. Oh Why) was a South Korean boy band."
        assert "boy band" in classify_en([], lead, None)["kinds"]


class TestParseYearsActiveEn:
    @pytest.mark.parametrize(
        "raw,expected_end,expected_ongoing",
        [
            ("2012–2021", 2021, False),
            ("2012–present", None, True),
            ("2010-current", None, True),
            ("2012–2016, 2019–2021", 2021, False),
            ("2015", None, False),
            ("", None, False),
            (None, None, False),
        ],
    )
    def test_終了年と現役判定(self, raw, expected_end, expected_ongoing):
        end, ongoing = parse_years_active_en(raw)
        assert end == expected_end
        assert ongoing == expected_ongoing


class TestDetectDisbandYear:
    @pytest.mark.parametrize(
        "lead,expected",
        [
            ("The group disbanded in 2019.", 2019),
            ("The group was dissolved in 2020.", 2020),
            ("They split up in 2015.", 2015),
            ("In 2021, the group disbanded.", 2021),
            ("The group is still active.", None),
            ("", None),
        ],
    )
    def test_解散年を拾う(self, lead, expected):
        assert detect_disband_year(lead) == expected
