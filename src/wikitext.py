"""wikitext から Infobox のフィールド値を取り出す。

素朴に `^\\|\\s*名前\\s*=\\s*(.*)$` で取ると、値が複数行に渡るテンプレート
({{Plainlist|...}} など) で 1 行目しか取れず、実測では `{{Plainlist` という
文字列だけが返っていた。テンプレートとリンクの入れ子を数えて、
深さ 0 で次のフィールド区切り `|` が現れるまでを値とする。

日本語版 Wikipedia には {{Infobox Musician}} (日本語フィールド名) と
{{Infobox musical artist}} (英語フィールド名) が混在するため、
呼び出し側は必ず日英のエイリアスをまとめて渡すこと。
"""
import re

# フィールド名は日本語・英語・アンダースコア・空白を含む。
# ★ 文字クラスを `ァ-ヶ` で書くと長音符「ー」(U+30FC) が範囲外になり、
#   「レーベル」「メンバー」がフィールドとして認識されない。認識に失敗すると
#   値の終端判定も効かず、次のフィールドの中身まで値に混入する。`\w` は
#   長音符・々を含むので、こちらを使う (中黒「・」だけは \w に入らないので追加)。
FIELD_START = re.compile(r"^[ \t]*\|[ \t]*([\w ・]+?)[ \t]*=", re.M)


def _value_end(text, start):
    """値の終端位置を返す。入れ子の外側で次のフィールド区切りが来る所まで。"""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        two = text[i : i + 2]
        if two in ("{{", "[["):
            depth += 1
            i += 2
            continue
        if two in ("}}", "]]"):
            depth -= 1
            i += 2
            # Infobox 自体の閉じ括弧に達した
            if depth < 0:
                return i - 2
            continue
        if text[i] == "\n" and depth == 0:
            # 次行がフィールド区切りなら、この改行で値は終わり
            m = FIELD_START.match(text, i + 1)
            if m:
                return i
            # テンプレートの終了 (}} で始まる行) でも終わり
            if text[i + 1 :].lstrip().startswith("}}"):
                return i
        i += 1
    return n


def extract_field(wikitext, aliases):
    """フィールドの生値を返す。見つからなければ None。

    aliases は候補フィールド名のリスト。最初に見つかったものを採る。
    """
    if not wikitext:
        return None
    for m in FIELD_START.finditer(wikitext):
        if m.group(1) not in aliases:
            continue
        start = m.end()
        return wikitext[start : _value_end(wikitext, start)].strip()
    return None


def clean_value(value):
    """表示用に装飾を落とす。年の抽出には使うが、判定語は残す。

    <br> は区切りとして意味があるので改行に変換する。
    HTML コメントは編集者向けの注記なので、年の判定を誤らせる前に消す。
    """
    if not value:
        return ""
    v = re.sub(r"<!--.*?-->", " ", value, flags=re.S)
    v = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", " ", v, flags=re.S)
    v = re.sub(r"<br\s*/?>", "\n", v, flags=re.I)
    # リンクは表示側 (| の後ろ) を残す
    v = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", v)
    # 箇条書きテンプレートは中身だけ残す
    v = re.sub(r"\{\{\s*(?:Plainlist|Hlist|Hlist-comma|ublist|unbulleted list)\s*\|", " ", v, flags=re.I)
    v = re.sub(r"\{\{[^{}]*\}\}", " ", v)
    v = v.replace("{{", " ").replace("}}", " ")
    v = re.sub(r"''+", "", v)
    v = re.sub(r"^[ \t*|]+", "", v, flags=re.M)
    v = re.sub(r"[ \t]+", " ", v)
    return v.strip(" |\n")
