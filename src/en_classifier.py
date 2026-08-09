"""en.wikipedia 版の判定ロジック (韓国の主分析と、日本の英語版対称化の両方で使う)。

日本語版とは使えるシグナルが違うので別実装にする:

- 年別カテゴリ (Musical groups established/disestablished in YYYY) が付与率 91.9% で使える
- Infobox years_active の保有率が 99.3% と高い
- ★ **冒頭定義文の時制で現存と解散を書き分ける慣行がある** ("is a" / "was a")
  日本語版に無いシグナルで、実測では他の 2 ソースが捉えない死亡を 71 件拾った

英語のピリオドは略語にも使われるため、文の切り方に注意が要る。
実例: "BTS (Korean: 방탄소년단; RR: Bangtan sonyeondan; lit." で切ると
主節に届かず、BTS の種別も時制も判定できない。
"""
import re

# --- 種別 -------------------------------------------------------------------
# 種別は冒頭全体を見る。'B.O.Y' のように略語のピリオドで文が切れる記事があり、
# 第 1 文に限定すると取りこぼす。語が現れる位置は判定に影響しない
IDOL_KINDS = {
    "boy band": r"\bboy band\b",
    "girl group": r"\bgirl group\b",
    "idol group": r"\bidol\b",
    "vocal group": r"\bvocal group\b",
    "duo/trio": r"\b(duo|trio)\b",
}
# K-pop アイドルとは言い難いもの。ただし boy band / girl group の言及があれば
# そちらを優先する (アイドルでありバンド編成、というグループが実在する)
NON_IDOL_KINDS = {
    "rock/indie band": r"\b(rock band|indie band|alternative rock|punk band|metal band|indie duo)\b",
    "project/producer": r"\b(producer group|project group)\b",
}

# --- 時制 -------------------------------------------------------------------
TENSE = re.compile(r"\b(is|was|are|were)\b")

# --- 年 ---------------------------------------------------------------------
YEAR_EST = re.compile(r"^Musical groups established in (\d{4})$")
YEAR_DIS = re.compile(r"^Musical groups disestablished in (\d{4})$")

# リード文から解散年を拾う。解散カテゴリと両方ある 81 件で ±1 年の一致率 96.3%
DISBAND_AFTER = re.compile(
    r"(?:disband|dissolv|split up|broke up|ceased|terminat|disestablish)[a-z]*"
    r"[^.]{0,60}?\b(19\d{2}|20\d{2})\b", re.I)
DISBAND_BEFORE = re.compile(
    r"\b(19\d{2}|20\d{2})\b[^.]{0,40}?(?:disband|dissolv|split up|broke up|disestablish)", re.I)


def first_sentence(lead):
    """冒頭の定義文。ピリオドの後に空白 + 大文字が続く場合のみ文末とみなす。"""
    s = re.sub(r"\s+", " ", lead or "")
    m = re.search(r"\.\s+(?=[A-Z])", s)
    return (s[: m.start() + 1] if m else s)[:400]


def _year_from_categories(categories, pattern):
    ys = [int(m.group(1)) for c in categories if (m := pattern.match(c))]
    return min(ys) if ys else None


def normalize_years_active(raw):
    """years_active の生値を、年が素で並んだ文字列に均す。

    🔴 `{{start date|2012}}` は中に開始年を抱えている。テンプレートを丸ごと落とすと
    '{{Start date|2012}}–2021' が ' –2021' になり、開始年が消えるだけでなく残った
    2021 を「唯一の年」と誤読して終了年の判定まで壊れる (2026-08-09 に実測して発覚)。
    テンプレートを消す前に start date の年を取り出しておくこと。
    """
    if not raw:
        return ""
    v = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    v = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", " ", v, flags=re.S)
    v = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", v)
    # {{start date|YYYY|MM|DD}} / {{end date|YYYY}} 等は年だけ残す
    v = re.sub(r"\{\{\s*(?:start|end)[ _]?date[^|}]*\|\s*(\d{4})[^}]*\}\}", r" \1 ", v, flags=re.I)
    v = re.sub(r"\{\{[^{}]*\}\}", " ", v)
    return v


def parse_years_active_en(raw):
    """英語版 Infobox の years_active から終了年を取る。

    '2012–2021' / '2012–present' / '2012–2016, 2019–2021' 等。
    present/current の語があるか、最後の年より後ろに区切りがあれば現役。
    """
    if not raw:
        return None, False
    v = normalize_years_active(raw)
    if re.search(r"present|current", v, re.I):
        return None, True
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", v)]
    if not years:
        return None, False
    tail = v[v.rfind(str(years[-1])) + 4 :]
    if re.search(r"[-–—]", tail):
        return None, True
    return (years[-1], False) if len(years) >= 2 else (None, False)


def parse_years_active_start_en(raw):
    """years_active の開始年 (デビューの代理指標)。"""
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", normalize_years_active(raw))
    return int(years[0]) if years else None


def detect_disband_year(lead):
    """リード文から解散年を拾う。"""
    s = re.sub(r"\s+", " ", lead or "")
    m = DISBAND_AFTER.search(s) or DISBAND_BEFORE.search(s)
    return int(m.group(1)) if m else None


def classify_en(categories, lead, years_active_raw):
    """1 記事分の判定結果を返す。"""
    cats = list(categories or [])
    whole = re.sub(r"\s+", " ", lead or "")[:400]
    first = first_sentence(lead)

    kinds = [k for k, p in IDOL_KINDS.items() if re.search(p, whole, re.I)]
    non_idol = [k for k, p in NON_IDOL_KINDS.items() if re.search(p, whole, re.I)]

    m = TENSE.search(first)
    tense = m.group(1) if m else None
    is_past = tense in ("was", "were")

    ya_end, ya_ongoing = parse_years_active_en(years_active_raw)
    cat_est = _year_from_categories(cats, YEAR_EST)
    cat_dis = _year_from_categories(cats, YEAR_DIS)
    lead_dis = detect_disband_year(lead)

    # 死亡年は「独立性の高い順」に採る。カテゴリ > Infobox > リード文
    death_year = cat_dis or ya_end or (lead_dis if is_past else None)

    return {
        "kinds": kinds,
        "non_idol_kinds": non_idol,
        # バンド表記があっても boy band / girl group と書かれていればアイドルとして残す
        "is_idol": bool(kinds) or not non_idol,
        "is_idol_explicit": bool(kinds),
        "tense": tense,
        "is_past_tense": is_past,
        "cat_formed_year": cat_est,
        "cat_dissolved_year": cat_dis,
        "ya_end_year": ya_end,
        "ya_ongoing": ya_ongoing,
        "lead_dissolved_year": lead_dis,
        "death_year": death_year,
        # 死亡と分かるのに年が特定できないケース。打ち切り扱いにすると
        # 生存率を過大推定するので、件数を必ず報告する
        "death_without_year": is_past and death_year is None,
        "lead_first": first,
    }
