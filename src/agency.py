"""Infobox の事務所フィールドから事務所名を取り出す (Cox の共変量用)。

★ 事務所は**アイドル判定には使わない** (PLAN の Rejected Alternatives 参照)。
   手作りリストの恣意性と循環参照が理由で、その判断は変わらない。
   ここで抽出するのは Cox 比例ハザードの共変量「事務所規模」のためだけ。

値は表記が荒い。実測で見つかった形:

    'ジャニーズ事務所→SMILE-UP.（1995年 - 2024年）\\nSTARTO ENTERTAINMENT（2024年 - ）'
    '<ol><li>ジャニーズ事務所<li>SMILE-UP. (2015年 - 2024年)<li>STARTO ENTERTAINMENT</ol>'
    'ホリプロ \\n太田プロダクション \\nボックスコーポレーション \\nプロダクション尾木など'
    '韓国：Illusion\\n日本：株式会社伝元'
    '無所属（セルフプロデュース）'

値は時系列順に並ぶ慣行なので、**先頭を結成時の事務所**として採る。

★ 末尾文字を strip するときに長音符「ー」(U+30FC) を混ぜてはいけない。
  「アップフロントエージェンシー」が「アップフロントエージェンシ」になり、
  同じ事務所が 2 つに割れる。見た目が似ている「―」(U+2015)「−」(U+2212) とは別物。
"""
import re

# 値の区切り。改行・矢印・読点・箇条書きタグ
SPLIT = re.compile(r"[\n、,;；]|→|->|<li>|</?ol>|</?ul>")

# 落とす装飾
DROP_TAGS = re.compile(r"<[^>]+>")
DROP_COMMENT = re.compile(r"<!--.*?-->", re.S)
DROP_REF = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.S)
BR = re.compile(r"<br\s*/?>", re.I)
# 年の範囲・注記
DROP_PAREN = re.compile(r"[（(][^（()）]*[)）]")
# 内部リンクは表示側 (| の後ろ) を残す
WIKILINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")
# 外部リンク [https://example.com 表示名] は表示名だけ残す。
# 表示名が無い場合は URL ごと落とす
EXTLINK = re.compile(r"\[(?:https?:|//)\S*(?:\s+([^\]]*))?\]")
# 箇条書きテンプレートは中身だけ残す
LIST_TEMPLATE = re.compile(
    r"\{\{\s*(?:Plainlist|Hlist|Hlist-comma|ublist|unbulleted list|flatlist)\s*\|", re.I)
TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
# 「韓国：Illusion」のような国名ラベル
DROP_LABEL = re.compile(r"^\s*(?:韓国|日本|中国|台湾|米国|アメリカ)\s*[：:]\s*")
# 法人格。表記ゆれを吸収するため名前から落とす
CORP = re.compile(
    r"株式会社|㈱|\(株\)|（株）|有限会社|合同会社|合資会社|一般社団法人|"
    r"\bInc\.?|\bLtd\.?|\bCo\.,?\s*Ltd\.?|\bLLC\b|\bCorp\.?", re.I)
# 末尾の注記
DROP_SUFFIX = re.compile(r"(?:など|ほか|他|所属|系列)\s*$")
# 事務所名として意味を成さない値
NOISE = re.compile(
    r"^(?:なし|無し|不明|未定|同上|各所属事務所を参照|"
    r"各メンバーの所属は所属事務所およびメンバーを参照|[-−―\s.]*)$")

# 事務所を持たないことを表す値。欠損ではなく「無所属」という情報なので残す
INDEPENDENT = re.compile(r"^(?:無所属|インディーズ|セルフプロデュース|独立|フリー(?:ランス)?$)")
INDEPENDENT_LABEL = "無所属"

# 末尾から落とす文字。**長音符「ー」(U+30FC) は絶対に入れない**
TRIM_CHARS = " \t.,、。・'\"’”|*：:-−―"

# 同一企業の表記ゆれ・改称。「事務所規模」を測る変数なので、同じ会社が
# 2 つに割れると最も大きい事務所ほど規模を過小評価する。
# ★ ここに載せるのは wikitext 中に改称の連鎖 (A→B) が実際に現れるか、
#   単なる表記の違い (カナ/ラテン文字) であることが値から明らかなものだけ。
#   判定には使わないので、母集団の恣意性には影響しない。
ALIASES = {
    # ジャニーズ事務所 → SMILE-UP. → STARTO ENTERTAINMENT (値に改称連鎖が出る)
    "SMILE-UP.": "ジャニーズ事務所",
    "SMILE-UP": "ジャニーズ事務所",
    "STARTO ENTERTAINMENT": "ジャニーズ事務所",
    "STARTO ENTERTAINMENT.": "ジャニーズ事務所",
    # エイベックス系
    "エイベックス・エンタテインメント": "エイベックス",
    "エイベックス・マネジメント": "エイベックス",
    "エイベックス・ヴァンガード": "エイベックス",
    # カナ表記とラテン文字表記の併存
    "ASOBISYSTEM": "アソビシステム",
    "WACK Inc": "WACK",
}


def _preclean(raw):
    """wikitext の装飾を落として、区切りだけが残る形にする。"""
    v = DROP_COMMENT.sub(" ", raw)
    v = DROP_REF.sub(" ", v)
    v = BR.sub("\n", v)
    v = WIKILINK.sub(r"\1", v)
    v = EXTLINK.sub(lambda m: m.group(1) or " ", v)
    v = LIST_TEMPLATE.sub(" ", v)
    v = TEMPLATE.sub(" ", v)
    return v.replace("{{", " ").replace("}}", " ")


def normalize_agency(name):
    """事務所名を正規化する。名前として使えなければ None。"""
    if not name:
        return None
    s = DROP_TAGS.sub(" ", name)
    s = DROP_PAREN.sub(" ", s)
    s = DROP_LABEL.sub("", s)
    # 「※」以降は注記なので落とす
    s = s.split("※")[0].replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip(TRIM_CHARS)
    if not s or NOISE.match(s):
        return None
    # ★ 無所属の判定は DROP_SUFFIX より先。後にすると接尾辞「所属」が
    #   「無所属」を食って「無」だけが残り、欠損として捨てられる
    if INDEPENDENT.match(s):
        return INDEPENDENT_LABEL
    s = CORP.sub("", s)
    # 接尾辞を落として空になるなら、それは事務所名ではなく注記だけの値
    trimmed = DROP_SUFFIX.sub("", s).strip(TRIM_CHARS)
    s = trimmed if trimmed else s
    s = re.sub(r"\s+", " ", s).strip(TRIM_CHARS)
    # 1 文字は略記の残骸とみなす
    if len(s) < 2 or NOISE.match(s):
        return None
    return ALIASES.get(s, s)


def extract_agencies(raw_value):
    """事務所フィールドの生値から、正規化済みの事務所名を出現順に返す。"""
    if not raw_value:
        return []
    out = []
    for part in SPLIT.split(_preclean(raw_value)):
        name = normalize_agency(part)
        if name and name not in out:
            out.append(name)
    return out


def primary_agency(raw_value):
    """結成時の事務所。値は時系列順に並ぶ慣行なので先頭を採る。"""
    names = extract_agencies(raw_value)
    return names[0] if names else None
