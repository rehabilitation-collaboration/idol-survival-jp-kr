"""時計の起点を結成年から活動開始年 (デビュー代理) に変えて 7 年ピークを再検証する。

GPT 査読 round-1 の指摘 3 への対応。

  「7 年契約を論じるのに時計の起点が契約締結でもデビューでもなく結成年なのは
   中心仮説に直撃する。契約開始が結成から 1-2 年ずれるなら、契約由来ならピークは
   7 年目ではなく 8-9 年目にずれてもおかしくない」

英語版 Infobox の `years_active` 開始年をデビューの代理指標として使い、

  (a) 結成年カテゴリと years_active 開始年がどれだけずれるか
  (b) デビュー起点に張り替えても t = 7 の超過が残るか

を測る。ずれが 0 年中心なら「結成年 ≒ デビュー年」であり、指摘は緩和される。
ずれが 1-2 年あるなら、デビュー起点でピークが t = 7 に立つかどうかが決定的になる。

    .venv/bin/python scripts/probe_debut_clock.py
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import survival_analysis as sa  # noqa: E402
from en_classifier import classify_en, parse_years_active_start_en  # noqa: E402
from wikitext import extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "results", "debut_clock_check.md")
PAGES = {
    "KR": os.path.join(ROOT, "data", "raw", "en_kr_pages.jsonl"),
    "JP": os.path.join(ROOT, "data", "raw", "en_jp_pages.jsonl"),
}
YEARS_ACTIVE = ["years_active", "Years_active", "years active"]
WINDOW = (1996, 2025)
CENSOR_YEAR = 2026





def load(path):
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


def build(country):
    rows = []
    for p in load(PAGES[country]):
        raw_ya = extract_field(p.get("wikitext", ""), YEARS_ACTIVE)
        r = classify_en(p.get("categories", []), p.get("lead", ""), raw_ya)
        r["title"] = p["title"]
        r["ya_start_year"] = parse_years_active_start_en(raw_ya)
        rows.append(r)
    df = pd.DataFrame(rows)
    df = df[df["is_idol"] & df["cat_formed_year"].between(*WINDOW)].copy()
    df["formed_year"] = df["cat_formed_year"].astype(int)
    return df


def durations(df, start_col):
    """start_col を起点にした duration と event を返す。"""
    d = df[df[start_col].notna()].copy()
    d["start"] = d[start_col].astype(int)
    # 死亡年が起点より前になる行は使えない
    end = d["death_year"].fillna(CENSOR_YEAR).astype(float)
    ok = end >= d["start"]
    d = d[ok].copy()
    return (end[ok] - d["start"]).astype(int), d["death_year"].notna().astype(int), d


def excess(dur, ev, label):
    r = sa.excess_hazard_test(dur, ev, focus=7, neighbors=(5, 6, 8, 9))
    return {
        "母集団": label,
        "n": len(dur),
        "t=7 リスク集合": r["n_risk"],
        "t=7 死亡": r["deaths"],
        "h(7)": f"{r['hazard']*100:.1f}%",
        "近傍基準": f"{r['baseline_hazard']*100:.1f}%",
        "比": f"{r['ratio']:.2f}",
        "p": f"{r['p_value']:.3f}",
    }


def md_table(rows):
    """dict のリストを markdown 表にする (tabulate に依存しない)。"""
    if not rows:
        return ""
    cols = list(rows[0].keys())
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def main():
    lines = ["# 時計の起点をデビュー代理に張り替えた再検証", ""]
    lines.append("GPT 査読 round-1 指摘 3 への対応。`years_active` の開始年をデビューの代理として使う。")
    lines.append("")

    rows_shift, rows_test = [], []
    for country in ("KR", "JP"):
        df = build(country)
        have = df["ya_start_year"].notna()
        shift = (df.loc[have, "ya_start_year"].astype(int) - df.loc[have, "formed_year"])
        # 明らかな誤パースを除く (結成前に活動開始・20 年以上後にデビューは異常)
        sane = shift.between(-1, 10)
        rows_shift.append({
            "母集団": country,
            "n": len(df),
            "years_active 開始年あり": f"{int(have.sum())} ({have.mean()*100:.1f}%)",
            "ずれ 0 年": f"{(shift == 0).sum()} ({(shift == 0).mean()*100:.1f}%)",
            "ずれ 1 年": f"{(shift == 1).sum()} ({(shift == 1).mean()*100:.1f}%)",
            "ずれ 2 年以上": f"{(shift >= 2).sum()} ({(shift >= 2).mean()*100:.1f}%)",
            "負のずれ": int((shift < 0).sum()),
            "中央値": f"{shift[sane].median():.0f} 年",
        })

        # (1) 主分析: 全体を結成年起点
        d1, e1, _ = durations(df, "formed_year")
        rows_test.append(excess(d1, e1, f"{country} 全体・結成年起点 (主分析)"))

        # (2) 起点をデビュー代理に張り替え (years_active 開始年が取れる群のみになる)
        d2, e2, _ = durations(df, "ya_start_year")
        rows_test.append(excess(d2, e2, f"{country} 同群・活動開始年起点"))

        # (3) ★ 対照: (2) と同じ群を結成年起点で測る。
        #     (1) と (2) の違いが「起点の違い」なのか「部分集合の違い」なのかを分離する。
        sub = df[df["ya_start_year"].notna()].copy()
        d3, e3, _ = durations(sub, "formed_year")
        rows_test.append(excess(d3, e3, f"{country} 同群・結成年起点 (対照)"))

    lines.append("## 1. 結成年カテゴリと活動開始年のずれ")
    lines.append("")
    lines.append(md_table(rows_shift))
    lines.append("")

    lines.append("## 2. 起点を変えた t = 7 の超過ハザード検定")
    lines.append("")
    lines.append(md_table(rows_test))
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
