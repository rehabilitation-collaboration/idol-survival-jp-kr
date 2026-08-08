"""Infobox の事務所フィールドがどこまで取れるかを測る (Phase 5 の前処理)。

PLAN は Cox の共変量に「事務所規模」を要求しているが、どの parquet にも
事務所の列がない。抽出できるかをまず測る。

★ PLAN の Rejected Alternatives は「{{Plainlist}} で値が壊れる」ことを
   事務所リスト方式の却下理由の一つに挙げているが、これは入れ子を数える
   終端判定を入れる前の `src/wikitext.py` での実測だった。修正後の実力を測り直す。
   なお事務所を**判定に使わない**決定そのものは変わらない (共変量としてのみ使う)。

    python3 scripts/probe_agency.py

出力: results/probe_agency.txt
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agency import extract_agencies  # noqa: E402
from wikitext import clean_value, extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES = os.path.join(ROOT, "data", "raw", "ja_pages.jsonl")
POP = os.path.join(ROOT, "data", "jp_groups.parquet")
OUT = os.path.join(ROOT, "results", "probe_agency.txt")

AGENCY_FIELDS = ["事務所", "Production", "production", "所属事務所", "Agency", "agency"]


def main():
    import pandas as pd

    pop = set(pd.read_parquet(POP)["group_id"])
    raw_hits = 0
    parsed = {}
    broken = []
    with open(PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = rec.get("title")
            if rec.get("missing") or title not in pop or title in parsed:
                continue
            raw = extract_field(rec.get("wikitext", ""), AGENCY_FIELDS)
            names = extract_agencies(raw)
            parsed[title] = names
            if raw:
                raw_hits += 1
                if not names:
                    broken.append((title, clean_value(raw)[:80]))

    n = len(pop)
    got = sum(1 for v in parsed.values() if v)
    lines = []
    a = lines.append
    a("# Infobox 事務所フィールドの抽出実測 (Phase 5 前処理)")
    a("")
    a(f"母集団 {n} 件 / 記事を取得できた {len(parsed)} 件")
    a(f"- フィールドあり (生値): {raw_hits} 件 ({raw_hits / n:.1%})")
    a(f"- **正規化後に事務所名を取得: {got} 件 ({got / n:.1%})**")
    a(f"- 生値はあるが名前が取れない: {len(broken)} 件")
    a("")
    a("## 名前が取れなかった生値 (先頭 20 件)")
    a("")
    for t, v in broken[:20]:
        a(f"- `{t}`: {v!r}")
    a("")

    counts = Counter(nm for v in parsed.values() for nm in v)
    a(f"## 事務所の異なり数: {len(counts)}")
    a("")
    a("### 所属グループ数 上位 40")
    a("")
    a("| 事務所 | グループ数 |")
    a("|---|---|")
    for name, c in counts.most_common(40):
        a(f"| {name} | {c} |")
    a("")
    sizes = Counter(counts.values())
    a("### 規模の分布 (事務所あたりのグループ数)")
    a("")
    a("| グループ数 | 該当事務所数 |")
    a("|---|---|")
    for k in sorted(sizes):
        a(f"| {k} | {sizes[k]} |")
    a("")

    text = "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
