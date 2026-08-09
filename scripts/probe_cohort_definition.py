"""コホート定義がアウトカムに依存していないかを実測する (GPT 査読 round-1 指摘 1)。

査読で「結成年カテゴリと解散年カテゴリの union から母集団を作っているので、
解散すると母集団に入りやすくなる outcome-dependent sampling ではないか」と指摘された。

実装を読むと `formed_year_cat.between(...)` で窓を切っており、between は NaN に False を
返すため、結成年カテゴリを持たない記事は母集団に入らない。つまり union は「取得範囲」であって
「コホート定義」ではない。これを数字で確認し、あわせて

  「解散年カテゴリはあるが結成年カテゴリがないアイドル群」= 死亡が分かっているのに落ちている群

が何件あるかを測る。こちらは outcome-dependent inclusion とは逆向き (死亡例の脱落) のバイアスになる。

    .venv/bin/python scripts/probe_cohort_definition.py
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from en_classifier import classify_en  # noqa: E402
from idol_classifier import classify  # noqa: E402
from wikitext import extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
JA_PAGES = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
OUT = os.path.join(ROOT, "results", "cohort_definition_check.md")

# 英語版は国ごとに別ファイル。build_en_population.py と同じ入力を使う
EN_PAGES = {
    "KR (en.wikipedia)": os.path.join(ROOT, "data", "raw", "en_kr_pages.jsonl"),
    "JP (en.wikipedia)": os.path.join(ROOT, "data", "raw", "en_jp_pages.jsonl"),
}
YEARS_ACTIVE = ["years_active", "Years_active", "years active"]

YEARS = (1996, 2025)


def load_jsonl(path):
    rows, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] in seen:
                continue
            seen.add(rec["title"])
            rows.append(rec)
    return rows


def jp_table():
    rows = []
    for p in load_jsonl(JA_PAGES):
        r = classify(p.get("categories", []), p.get("lead", ""))
        r["title"] = p["title"]
        rows.append(r)
    df = pd.DataFrame(rows)
    idol = df[df["is_idol"]].copy()

    f = idol["formed_year_cat"]
    d = idol["dissolved_year_cat"]
    in_win_f = f.between(*YEARS)
    in_win_d = d.between(*YEARS)

    return idol, {
        "アイドル判定陽性": len(idol),
        "結成年カテゴリあり": int(f.notna().sum()),
        "結成年カテゴリなし": int(f.isna().sum()),
        "結成年カテゴリなし かつ 解散年カテゴリあり": int((f.isna() & d.notna()).sum()),
        "結成年カテゴリなし かつ 解散年カテゴリも窓内": int((f.isna() & in_win_d).sum()),
        "母集団 (結成年カテゴリが窓内)": int(in_win_f.sum()),
        "うち解散年カテゴリあり": int((in_win_f & d.notna()).sum()),
    }


def en_table(path):
    """英語版パネル。build_en_population.py と同じ判定を通してから数える。"""
    rows = []
    for p in load_jsonl(path):
        r = classify_en(p.get("categories", []), p.get("lead", ""),
                        extract_field(p.get("wikitext", ""), YEARS_ACTIVE))
        r["title"] = p["title"]
        rows.append(r)
    df = pd.DataFrame(rows)
    idol = df[df["is_idol"]].copy()

    f = idol["cat_formed_year"]
    d = idol["cat_dissolved_year"]
    return {
        "アイドル判定陽性": len(idol),
        "結成年カテゴリあり": int(f.notna().sum()),
        "結成年カテゴリなし": int(f.isna().sum()),
        "結成年カテゴリなし かつ 解散年カテゴリあり": int((f.isna() & d.notna()).sum()),
        "母集団 (結成年カテゴリが窓内)": int(f.between(*YEARS).sum()),
    }


def main():
    idol, jp = jp_table()
    en = {name: en_table(path) for name, path in EN_PAGES.items()}

    lines = ["# コホート定義がアウトカム依存でないかの確認", ""]
    lines.append("GPT 査読 round-1 の指摘 1 (outcome-dependent sampling) に対する実測。")
    lines.append("")
    lines.append("## 結論")
    lines.append("")
    dropped = jp["結成年カテゴリなし かつ 解散年カテゴリあり"]
    lines.append(
        f"母集団に入るには**結成年カテゴリが観測窓内にあること**が必要で "
        f"(`formed_year_cat.between(1996, 2025)`・`between` は NaN に False を返す)、"
        f"解散年カテゴリだけを持つ記事は母集団に入らない。"
        f"実測でも母集団 {jp['母集団 (結成年カテゴリが窓内)']} 件は**全件が結成年カテゴリを持つ**。"
    )
    lines.append("")
    lines.append(
        f"したがって解散 (アウトカム) が組入れ確率を上げる構造にはなっていない。"
        f"ただし逆向きに、**解散年カテゴリはあるが結成年カテゴリがないアイドル群 {dropped} 件**が"
        f"母集団から落ちている。これは死亡例の系統的な脱落であり、離脱率を**過小推定**する方向に働く。"
    )
    lines.append("")
    lines.append("## 日本 (ja.wikipedia) の内訳")
    lines.append("")
    lines.append("| 区分 | 件数 |")
    lines.append("|---|---|")
    for k, v in jp.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines.append("## 英語版パネルの内訳 (同じ `cat_formed_year.between()` を使う)")
    lines.append("")
    keys = list(next(iter(en.values())).keys())
    lines.append("| 区分 | " + " | ".join(en.keys()) + " |")
    lines.append("|---|" + "---|" * len(en))
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(v[k]) for v in en.values()) + " |")
    lines.append("")
    lines.append(
        "英語版も母集団は結成年カテゴリ (`Musical groups established in YYYY`) が窓内のものに限られる。"
        "解散年カテゴリだけを持つ記事は入らない。"
    )
    lines.append("")

    # 落ちている群の実例
    f = idol["formed_year_cat"]
    d = idol["dissolved_year_cat"]
    lost = idol[f.isna() & d.notna()].sort_values("dissolved_year_cat")
    if len(lost):
        lines.append(f"### 落ちている {len(lost)} 件 (解散年は分かるが結成年カテゴリがない)")
        lines.append("")
        lines.append("| グループ | 解散年 |")
        lines.append("|---|---|")
        for _, r in lost.iterrows():
            lines.append(f"| {r['title']} | {int(r['dissolved_year_cat'])} |")
        lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
