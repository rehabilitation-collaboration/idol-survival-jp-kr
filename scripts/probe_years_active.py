"""母集団の Infobox「活動期間」がどう書かれているかを実測する。

Phase 2 のパーサを設計するための根拠。既知の 3 課題だけを見て書くと
母集団 1,346 件の実態を外すので、まず表記のパターンを数える。

    .venv/bin/python scripts/probe_years_active.py

出力: フィールド保有率・年の出現形・終了の表し方・パース不能例。
"""
import json
import os
import re
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wikitext import clean_value, extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
PARQUET = os.path.join(ROOT, "data", "jp_groups.parquet")

YEARS_ACTIVE = ["活動期間", "活動年数", "Years_active", "years_active", "Years active"]

YEAR = re.compile(r"(\d{4})\s*年?")
# 終了を示す語。日本は「解散」と「活動休止」が別物なので分けて数える
END_WORDS = {
    "解散": r"解散",
    "活動休止": r"活動休止|活動を休止",
    "無期限休止": r"無期限",
    "活動終了": r"活動終了|活動終了",
    "活動停止": r"活動停止",
    "終了": r"終了",
    "現在": r"現在|現役",
}
DASH = r"[-–—―ー～〜~]"


def load_wikitext(pop_ids):
    out = {}
    with open(PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] not in pop_ids:
                continue
            out.setdefault(rec["title"], rec.get("wikitext", ""))
    return out


def main():
    pop = pd.read_parquet(PARQUET)
    texts = load_wikitext(set(pop["group_id"]))
    print(f"母集団 {len(pop)} 件 / wikitext 取得済 {len(texts)} 件\n")

    raw_vals, has_field = {}, 0
    for title, wt in texts.items():
        v = extract_field(wt, YEARS_ACTIVE)
        if v is not None:
            has_field += 1
            raw_vals[title] = v

    n = len(texts)
    print(f"--- フィールド保有率 ---")
    print(f"  活動期間フィールドあり: {has_field}/{n} ({has_field/n:.1%})\n")

    # 値の形を分類する
    shapes = Counter()
    end_word_hits = Counter()
    multiline = 0
    no_year = []
    single_year = []
    range_year = []

    for title, raw in raw_vals.items():
        v = clean_value(raw)
        if "\n" in v:
            multiline += 1
        years = YEAR.findall(v)
        for label, pat in END_WORDS.items():
            if re.search(pat, v):
                end_word_hits[label] += 1
        if not years:
            shapes["年が1つも無い"] += 1
            no_year.append((title, v))
        elif re.search(rf"\d{{4}}\s*年?[^\n]*{DASH}[^\n]*\d{{4}}", v):
            shapes["範囲 (開始-終了 両方に年)"] += 1
            range_year.append((title, v))
        elif re.search(rf"\d{{4}}\s*年?[^\n]*{DASH}", v):
            shapes["開始のみ (ダッシュの後に年が無い = 現役)"] += 1
        else:
            shapes["年が1つだけ (ダッシュ無し)"] += 1
            single_year.append((title, v))

    print("--- 値の形 ---")
    for k, c in shapes.most_common():
        print(f"  {k:<40} {c:>5} ({c/max(has_field,1):.1%})")
    print(f"  {'複数行にまたがる値':<40} {multiline:>5} ({multiline/max(has_field,1):.1%})")

    print("\n--- 終了を示す語の出現 (重複あり) ---")
    for k, c in end_word_hits.most_common():
        print(f"  {k:<12} {c:>5}")

    print("\n--- 年が1つも無い例 (最大15件) ---")
    for t, v in no_year[:15]:
        print(f"  {t[:24]:<26} {v[:60]!r}")

    print("\n--- 年が1つだけの例 (最大15件) ---")
    for t, v in single_year[:15]:
        print(f"  {t[:24]:<26} {v[:60]!r}")

    print("\n--- 範囲表記の例 (最大12件) ---")
    for t, v in range_year[:12]:
        print(f"  {t[:24]:<26} {v[:70]!r}")

    print("\n--- 既知課題の再現確認 ---")
    for t in ["EBiDAN", "CURE'T", "Are 湯 Lady"]:
        if t in raw_vals:
            print(f"  {t}")
            print(f"    raw  : {raw_vals[t][:90]!r}")
            print(f"    clean: {clean_value(raw_vals[t])[:90]!r}")
        else:
            print(f"  {t}: 母集団に含まれない")


if __name__ == "__main__":
    main()
