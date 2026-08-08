"""英語版 Wikipedia から性別を決める (Phase 5 の前処理)。

Phase 3 が持っている `kind` 列 (boy band / girl group / duo/trio / unspecified) は
リード文由来なので、性別が書かれていない記事で落ちる (実測: 韓国 20% / 日本 40% が不明)。
カテゴリの方が付与率が高い (韓国 89.4% / 日本 86.7%) ので、こちらを主ソースにする。

    ソース A: カテゴリ (`South Korean boy bands` / `Japanese girl groups` 等)
    ソース B: リード文 (`is a South Korean boy band` 等)

日本語版と同じく 2 ソースで照合してから決める。カテゴリを優先するのは、
リード文が「duo」「R&B group」のように性別を書かない記事が多いため。

★ カテゴリは接尾辞で厳密に判定する。部分一致にすると同名カテゴリ
(`April (girl group)`・`Rainbow (girl group)`) や無関係なカテゴリ
(`Magical girl anime and manga`・`Lists of South Korean women`) を拾ってしまう。
"""
import re

# --- ソース A: カテゴリ -----------------------------------------------------
# 接尾辞での完全一致。`April (girl group)` は単数 + 括弧なので該当しない
MALE_CAT = re.compile(
    r"(?:^|\b)(?:boy bands|boy groups|male musical duos|male musical trios|"
    r"all-male bands|male vocal groups)$", re.I)
FEMALE_CAT = re.compile(
    r"(?:^|\b)(?:girl groups|all-female bands|all-female punk bands|"
    r"all-female metal bands|all-female hardcore punk bands|"
    r"female musical duos|female musical trios|female vocal groups)$", re.I)
MIXED_CAT = re.compile(
    r"(?:^|\b)(?:co-ed groups|mixed-gender bands|male–female musical duos|"
    r"male-female musical duos|mixed-gender musical duos|mixed-gender musical trios|"
    r"mixed-gender musical quartets|mixed-gender musical quintets|"
    r"mixed-gender musical sextets|mixed-gender musical septets)$", re.I)

# --- ソース B: リード文 -----------------------------------------------------
MALE_LEAD = re.compile(
    r"\bboy (?:band|group)\b|\bboyband\b|\ball-male\b|"
    r"\bmale (?:idol )?(?:group|band|duo|trio|quartet|vocal group)\b", re.I)
FEMALE_LEAD = re.compile(
    r"\bgirl (?:group|band)\b|\bgirlgroup\b|\ball-female\b|\ball-girl\b|"
    r"\bfemale (?:idol )?(?:group|band|duo|trio|quartet|vocal group)\b", re.I)
MIXED_LEAD = re.compile(r"\bco-ed\b|\bcoed\b|\bmixed[- ](?:gender|sex)\b", re.I)


def sex_from_categories(categories):
    """カテゴリ由来の性別。決まらなければ None。"""
    male = female = mixed = False
    for c in categories or []:
        c = c.strip()
        if MIXED_CAT.search(c):
            mixed = True
        elif MALE_CAT.search(c):
            male = True
        elif FEMALE_CAT.search(c):
            female = True
    if mixed:
        return "mixed"
    if male and female:
        # 男女両方のカテゴリが付くのは姉妹グループ・別名義の混入。
        # 断定できないので不明として扱い、リード文に判断を譲る
        return None
    if male:
        return "M"
    if female:
        return "F"
    return None


def sex_from_lead(lead):
    """リード文由来の性別。決まらなければ None。"""
    s = re.sub(r"\s+", " ", lead or "")[:600]
    if MIXED_LEAD.search(s):
        return "mixed"
    male = bool(MALE_LEAD.search(s))
    female = bool(FEMALE_LEAD.search(s))
    if male and female:
        return None
    if male:
        return "M"
    if female:
        return "F"
    return None


def infer_sex_en(categories, lead):
    """性別と、どのソースで決まったかを返す。

    戻り値: (sex, source)
        sex     'M' / 'F' / 'mixed' / 'unknown'
        source  'category' / 'lead' / 'none'
    """
    cat = sex_from_categories(categories)
    if cat:
        return cat, "category"
    lead_sex = sex_from_lead(lead)
    if lead_sex:
        return lead_sex, "lead"
    return "unknown", "none"
