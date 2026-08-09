"""活動期間パーサのテスト。

ケースは母集団 1,346 件の実測 (scripts/probe_years_active.py) と、
Phase 0 で見つかっていた既知の 3 課題から取っている。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wikitext import clean_value, extract_field  # noqa: E402
from years_active import detect_lead_end, parse_years_active  # noqa: E402


class TestParseYearsActive:
    def test_開始と終了の両方がある(self):
        r = parse_years_active("[[2014年]] - [[2024年]]")
        assert (r["start_year"], r["end_year"]) == (2014, 2024)
        assert r["is_ongoing"] is False

    def test_終了年がなければ現役として打ち切る(self):
        r = parse_years_active("[[2018年]] -")
        assert r["start_year"] == 2018
        assert r["end_year"] is None
        assert r["is_ongoing"] is True

    def test_年が1つだけなら終了年を立てない(self):
        # 終了の証拠が無い。死亡にすると生存期間を過小推定する
        r = parse_years_active("[[2008年]]")
        assert r["start_year"] == 2008
        assert r["end_year"] is None

    @pytest.mark.parametrize("raw", ["", "-", "   ", None])
    def test_値が空なら何も返さない(self, raw):
        r = parse_years_active(raw)
        assert r["start_year"] is None and r["end_year"] is None

    def test_HTMLコメントで現役判定を誤らない(self):
        # 既知課題: EBiDAN。コメントを残すと「解散」の語を拾ってしまう
        r = parse_years_active("[[2010年]] - <!-- 解散または活動終了の年まで -->")
        assert r["start_year"] == 2010
        assert r["end_year"] is None
        assert r["is_ongoing"] is True
        assert r["end_reason"] is None

    def test_Plainlistテンプレートでも値が取れる(self):
        # 既知課題: CURE'T。旧実装は '{{Plainlist|' しか取れなかった
        r = parse_years_active("{{Plainlist|\n*[[2025年]]11月24日 -（CURE'T）\n}}")
        assert r["start_year"] == 2025
        assert r["is_ongoing"] is True

    def test_startdateテンプレートでも値が取れる(self):
        # 🔴 2026-08-09 発覚。{{Start date|YYYY}} を一括除去に任せると年ごと消え、
        # 活動期間が丸ごと欠損になっていた (母集団 1,346 件中 10 件が該当)。
        # 同じ書式を en 側で取りこぼしていたのが発端で、日本側も調べて見つかった。
        r = parse_years_active("{{Start date|2009}} - {{End date|2018}}")
        assert r["start_year"] == 2009
        assert r["end_year"] == 2018

    def test_startdateテンプレートで終了年がなければ現役(self):
        r = parse_years_active("{{Start date|2013}}-")
        assert r["start_year"] == 2013
        assert r["end_year"] is None
        assert r["is_ongoing"] is True

    def test_startdateテンプレートと素の年の混在(self):
        r = parse_years_active("{{Start date|2023}} - 2025年（活動休止）")
        assert r["start_year"] == 2023
        assert r["end_year"] == 2025

    def test_終了年と活動停止の併記を両方取る(self):
        # 既知課題: Are 湯 Lady
        r = parse_years_active("2014年5月 - 2016年9月<br />※活動停止中")
        assert (r["start_year"], r["end_year"]) == (2014, 2016)
        assert r["end_reason"] == "hiatus"

    def test_複数期は最初の開始と最後の終了を採る(self):
        r = parse_years_active("1期 [[2014年]] - [[2016年]]<br />2期 [[2018年]] - [[2020年]]")
        assert (r["start_year"], r["end_year"]) == (2014, 2020)

    def test_複数期の最後が現役なら打ち切る(self):
        r = parse_years_active("1期 [[2014年]] - [[2016年]]<br />2期 [[2018年]] -")
        assert r["start_year"] == 2014
        assert r["end_year"] is None
        assert r["is_ongoing"] is True

    def test_現在の語があれば現役(self):
        r = parse_years_active("[[2015年]] - 現在")
        assert r["end_year"] is None
        assert r["is_ongoing"] is True

    def test_終了理由を拾う(self):
        assert parse_years_active("[[1996年]] - [[2016年]]（解散）")["end_reason"] == "dissolved"
        assert parse_years_active("[[2010年]] - [[2020年]] 無期限活動休止")["end_reason"] == "indefinite_hiatus"


class TestExtractField:
    def test_長音符を含むフィールド名を認識する(self):
        # ★ 旧実装は文字クラスを ァ-ヶ で書いていたため「レーベル」を認識できず、
        #   値の終端判定が効かずに次フィールドの中身まで混入していた
        wt = "{{Infobox Musician\n|活動期間 = [[2018年]] -\n|レーベル = avex trax\n}}"
        assert extract_field(wt, ["活動期間"]) == "[[2018年]] -"
        assert extract_field(wt, ["レーベル"]) == "avex trax"

    def test_複数行にまたがる値を最後まで取る(self):
        wt = "{{Infobox\n|活動期間 = {{Plainlist|\n*[[2014年]] - [[2016年]]\n}}\n|レーベル = x\n}}"
        v = extract_field(wt, ["活動期間"])
        assert "2016" in v
        assert "レーベル" not in v

    def test_存在しないフィールドはNone(self):
        assert extract_field("{{Infobox\n|事務所 = x\n}}", ["活動期間"]) is None

    def test_日英エイリアスのどちらでも取れる(self):
        wt = "{{Infobox musical artist\n|Years_active = [[2001年]] -\n}}"
        assert extract_field(wt, ["活動期間", "Years_active"]) == "[[2001年]] -"


class TestCleanValue:
    def test_リンクは表示側を残す(self):
        assert clean_value("[[2014年|平成26年]]") == "平成26年"

    def test_HTMLコメントを消す(self):
        assert "解散" not in clean_value("2010年 - <!-- 解散の年まで -->")

    def test_brは改行になる(self):
        assert "\n" in clean_value("a<br />b")


class TestDetectLeadEnd:
    @pytest.mark.parametrize(
        "lead,expected",
        [
            ("○○は、日本の女性アイドルグループ。2020年に解散した。", "dissolved"),
            ("○○は、日本の女性アイドルグループ。2020年より活動休止中。", "hiatus"),
            ("○○は、日本の女性アイドルグループ。2020年に無期限活動休止を発表。", "indefinite_hiatus"),
            ("○○は、日本の女性アイドルグループ。2020年に活動終了。", "ended"),
            ("○○は、日本の女性アイドルグループ。", None),
            ("", None),
        ],
    )
    def test_リード文から終了種別を検出(self, lead, expected):
        assert detect_lead_end(lead) == expected
