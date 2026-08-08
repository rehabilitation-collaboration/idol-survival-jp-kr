"""Phase 5 レポートの共通部品。

`report_sections.py` (標準的な生存分析の節) と
`report_hazard.py` (7 年ハザード集中の節) の両方から使う。
"""

LABELS = {
    "jp_ja": "日本 ja.wikipedia (主分析)",
    "kr_en": "韓国 en.wikipedia (主分析)",
    "jp_en": "日本 en.wikipedia (感度分析)",
}


def fmt_p(p):
    """p 値の表記。0.001 未満は丸めずに不等号で書く。"""
    return "< 0.001" if p < 0.001 else f"{p:.3f}"
