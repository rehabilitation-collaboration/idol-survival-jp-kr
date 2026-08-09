"""英語版 Infobox の `label` から所属先 (レーベル / 事務所) を取り出す。

査読で「K-pop では同一 agency の群が独立とは考えにくいので、agency-clustered SE や
leave-one-agency-out を足すべき」と指摘された。韓国側にも所属を表す列が要る。

en.wikipedia の K-pop 記事は `agency` フィールドをまったく持たない (実測 0/641) が、
`label` は 94.7% が持つ。K-pop は制作事務所がそのままレーベルであることが多いので、
label をクラスタ変数の代理として使う。**正確な事務所名ではない**ので、
クラスタリングの単位としてのみ使い、係数を解釈しない。

表記ゆれの正規化が要る: 実測で `SM` と `SM Entertainment` が別クラスタに割れ、
`{{flatlist|...}}` のテンプレート名が値として残っていた。
"""
import re

from wikitext import clean_value

# 値ではなくテンプレート名が残ったもの。クラスタ名にしてはいけない
TEMPLATE_NOISE = {
    "flatlist", "plainlist", "hlist", "ublist", "unbulleted list",
    "nowrap", "startflatlist", "endflatlist", "collapsible list",
}

# 会社形態を表す接尾辞。落として比較しないと SM と SM Entertainment が割れる
SUFFIX = re.compile(
    r"\s*(?:entertainment|ent\.?|music|musics|records?|recordings?|company|co\.?|"
    r"inc\.?|ltd\.?|corp\.?|corporation|group|label|labels|media|studios?|"
    r"productions?|agency|communications?)\s*$",
    re.I,
)


def normalize_label(name):
    """比較用のキーに均す。会社形態の接尾辞を繰り返し落とす。"""
    if not name:
        return None
    s = re.sub(r"\s+", " ", name).strip(" .,'\"|*:-–—")
    if not s or s.lower() in TEMPLATE_NOISE:
        return None
    prev = None
    while prev != s:
        prev = s
        s = SUFFIX.sub("", s).strip(" .,&|-")
    s = s.strip()
    # 1 文字まで削れたものは元に戻す (例: 略称のみのケースを潰しすぎない)
    return s if len(s) >= 2 else re.sub(r"\s+", " ", name).strip(" .,'\"|*:-–—")


def primary_label(raw_value):
    """label フィールドの生値から主たる所属先を 1 つ返す。

    複数レーベルが並ぶ場合は先頭を採る。所属の履歴ではなく
    「どの系列に属するか」をクラスタとして拾いたいだけなので先頭で足りる。
    """
    if not raw_value:
        return None
    s = clean_value(raw_value)
    if not s:
        return None
    # 箇条書き・区切りで分割し、最初の実体を採る
    for part in re.split(r"[,;\n]|<br\s*/?>|\s+•\s+", s):
        part = re.sub(r"\(.*?\)", "", part)
        name = normalize_label(part)
        if name:
            return name
    return None
