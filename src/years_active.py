"""Infobox「活動期間」から活動の開始と終了を取り出す。

母集団 1,346 件に対する実測 (scripts/probe_years_active.py) で、値は
おおよそ次の 4 形に分かれる:

    範囲 (開始と終了の両方に年)          48.6%   例 '2014年 - 2024年'
    開始のみ (ダッシュの後に年が無い)      48.7%   例 '2018年 -'
    年が 1 つだけ (ダッシュ無し)          1.4%   例 '2008年'
    年が 1 つも無い (実質欠損)            1.3%   例 '' / '-'

「年が 1 つだけ」は終了の証拠が無いので打ち切りとして扱う。
終了年があると誤読して死亡にすると、生存期間を過小推定してしまう。
"""
import re

from wikitext import clean_value

DASH = r"[-–—―ー~～〜]"
YEAR = re.compile(r"(\d{4})\s*年")

# 活動期間フィールドの中に終了の理由が書かれることがある (実測では少数)
END_WORDS = {
    "dissolved": r"解散",
    "indefinite_hiatus": r"無期限",
    "hiatus": r"活動休止|活動を休止|活動停止",
    "ended": r"活動終了|活動を終了",
}


def _match_positions(text):
    """(年, 終端位置) を出現順に返す。"""
    return [(int(m.group(1)), m.end()) for m in YEAR.finditer(text)]


def parse_years_active(raw):
    """活動期間の生値を解釈する。

    生存分析は年単位で行う (Kim 2026 も年単位) ため、月日は解釈しない。

    返り値:
        start_year / end_year   int or None
        is_ongoing              最後の年より後ろに区切りがあり終了年が無い
        end_reason              フィールド内に書かれた終了理由 (あれば)
        n_years                 抽出できた年の個数 (診断用)
    """
    empty = {
        "start_year": None, "end_year": None,
        "is_ongoing": False, "end_reason": None, "n_years": 0, "raw_clean": "",
    }
    v = clean_value(raw)
    if not v:
        return empty

    positions = _match_positions(v)
    if not positions:
        return {**empty, "raw_clean": v}

    years = [y for y, _ in positions]
    start_year = years[0]
    last_year, last_end = positions[-1]

    # 最後の年より後ろに区切り記号があれば「以降も継続」を意味する。
    # 「2018年 -」は現役、「2014年 - 2024年」は 2024 で終了。
    tail = v[last_end:]
    ongoing = bool(re.search(DASH, tail)) or bool(re.search(r"現在|現役", v))

    if ongoing or len(years) < 2:
        # 年が 1 つだけの場合も終了の証拠が無いので打ち切り扱いにする
        end_year = None
    else:
        end_year = last_year

    end_reason = None
    for key, pat in END_WORDS.items():
        if re.search(pat, v):
            end_reason = key
            break

    return {
        "start_year": start_year,
        "end_year": end_year,
        "is_ongoing": ongoing,
        "end_reason": end_reason,
        "n_years": len(years),
        "raw_clean": v,
    }


# リード文に書かれる終了表現。活動期間フィールドには終了理由がほとんど
# 書かれていない (実測で活動休止 11 件・解散 2 件) ため、
# 緩和定義の材料はリード文から取る。
LEAD_END_PATTERNS = {
    "indefinite_hiatus": r"無期限[のな]?活動休止|活動を無期限",
    "hiatus": r"活動休止|活動を休止|活動停止",
    "ended": r"活動終了|活動を終了",
    "dissolved": r"解散",
}


def detect_lead_end(lead):
    """リード文から終了の種類を検出する。強い順に 1 つ返す。"""
    if not lead:
        return None
    for key, pat in LEAD_END_PATTERNS.items():
        if re.search(pat, lead):
            return key
    return None
