"""グループ名の名寄せ。

RIAJ の認定作品に載るアーティスト名と Wikipedia の記事タイトルを突き合わせる。
両者は表記が揺れる (全角/半角・大文字小文字・記号・曖昧回避の括弧)。

正規化は「落としすぎない」ことを優先する。記号を全部落とすと
`w-inds.` と `Winds` のような別グループが衝突するため、
比較は正規化キーの完全一致のみで行い、部分一致は使わない。
"""
import re
import unicodedata

# Wikipedia の曖昧回避。'嵐 (グループ)' → '嵐'
DISAMBIG = re.compile(r"\s*[（(][^）)]*[）)]\s*$")
# 名寄せで無視する記号。長音符と句点はグループ名の一部なので残す
STRIP = re.compile(r"[\s　・･,，\-–—_'\"’”“／/\\!！?？*＊+＋~〜:：;；&＆]")


def normalize(name):
    """比較用のキーを作る。"""
    if not name:
        return ""
    s = unicodedata.normalize("NFKC", str(name))
    s = DISAMBIG.sub("", s)
    s = s.casefold()
    s = STRIP.sub("", s)
    return s


def build_index(names):
    """正規化キー -> 元の名前のリスト。"""
    idx = {}
    for n in names:
        idx.setdefault(normalize(n), []).append(n)
    return idx
