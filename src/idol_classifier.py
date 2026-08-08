"""アイドル判定ルール (PLAN「アイドル判定ルール」節の実装)。

判定は 2 つの独立したシグナル源の OR で行う:

    C1  アイドル系カテゴリへの所属
    C2  記事冒頭の定義文に「アイドル」
    C3  同定義文に「ダンス&ボーカル」等 (LDH 系が一貫して使う自称)

カテゴリ単独 (C1) は中核 ground truth の 51.9% しか拾わず、
STARTO/旧ジャニーズ 17 件と LDH 6 件が構造的に全滅する。
C2+C3 を足すと 96.2% になる (scripts/probe_lead_definition.py で実測)。

事務所名は判定に使わない。恣意的なリストが必要になるうえ、
{{Plainlist}} で値が壊れ、事務所改称も混入するため (PLAN の却下理由を参照)。
"""
import re

# --- 包含シグナル -----------------------------------------------------------

IDOL_CATEGORIES = {
    "日本の女性アイドルグループ",
    "日本の男性アイドルグループ",
    "日本のアイドルグループ",
    "アイドルグループ",
}

IDOL_PAT = re.compile(r"アイドル")
# LDH 系が一貫して名乗る「ダンス&ボーカルグループ」。表記ゆれ (& ＆ ・) を吸収する
DANCE_VOCAL_PAT = re.compile(
    r"ダンス\s*[&＆・]\s*ヴ?[ォボ]ーカル|ダンスボーカル|パフォーマンスグループ"
)

# --- 除外・分類シグナル -----------------------------------------------------

# 日本の母集団から外す (韓国側の母集団で扱う)。ground truth の K-POP 6 件を全件検出
KR_PAT = re.compile(r"韓国|大韓民国|K-POP|Kポップ")
SEIYU_PAT = re.compile(r"声優")
FEMALE_PAT = re.compile(r"女性|女子|ガールズ")
MALE_PAT = re.compile(r"男性|男子|ボーイズ")
MIXED_PAT = re.compile(r"男女")

FORMED_CAT = re.compile(r"^(\d{4})年に結成した音楽グループ$")
DISSOLVED_CAT = re.compile(r"^(\d{4})年に解散した音楽グループ$")


def first_sentence(lead):
    """冒頭の定義文を返す。

    最初の句点で切ると、記事名に句点を含むグループ (モーニング娘。) で
    述部が消える。定義文が「〜は、」で始まる慣行を利用し、述部側を優先して取る。
    """
    if not lead:
        return ""
    text = re.sub(r"\s+", " ", lead)
    m = re.search(r"は[、,](.{0,200}?[。])", text)
    if m:
        return m.group(0).strip()
    m = re.search(r"^(.{0,300}?[。])", text)
    return (m.group(1) if m else text[:200]).strip()


def _year_from_categories(categories, pattern):
    """カテゴリ由来の年。複数あれば最も早い年を採る。"""
    years = [int(m.group(1)) for c in categories if (m := pattern.match(c))]
    return min(years) if years else None


def infer_sex(categories, sentence):
    """性別。カテゴリを優先し、無ければ冒頭定義文に落とす。"""
    cats = set(categories)
    if "日本の女性アイドルグループ" in cats:
        return "F"
    if "日本の男性アイドルグループ" in cats:
        return "M"
    if MIXED_PAT.search(sentence):
        return "mixed"
    if FEMALE_PAT.search(sentence):
        return "F"
    if MALE_PAT.search(sentence):
        return "M"
    return "unknown"


def classify(categories, lead):
    """1 記事分の判定結果を返す。

    is_idol       主分析の母集団 (ルール D: C1 OR C2 OR C3、韓国を除外)
    is_idol_strict 感度分析用 (ルール C: C1 OR C2、ダンス&ボーカルを含めない)
    """
    cats = list(categories or [])
    s = first_sentence(lead)

    c1 = bool(set(cats) & IDOL_CATEGORIES)
    c2 = bool(IDOL_PAT.search(s))
    c3 = bool(DANCE_VOCAL_PAT.search(s))
    is_kr = bool(KR_PAT.search(s))

    return {
        "c1_category": c1,
        "c2_lead_idol": c2,
        "c3_dance_vocal": c3,
        "is_korean": is_kr,
        "is_seiyu": bool(SEIYU_PAT.search(s)),
        "is_idol": (c1 or c2 or c3) and not is_kr,
        "is_idol_strict": (c1 or c2) and not is_kr,
        # C1 と C2 の食い違い。母集団に対する割合が判定の不安定さの指標になる
        "signal_disagree": c1 != c2,
        "sex": infer_sex(cats, s),
        "formed_year_cat": _year_from_categories(cats, FORMED_CAT),
        "dissolved_year_cat": _year_from_categories(cats, DISSOLVED_CAT),
        "lead_sentence": s,
    }
