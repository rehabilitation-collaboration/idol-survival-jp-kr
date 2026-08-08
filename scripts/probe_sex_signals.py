"""英語版 Wikipedia から性別シグナルがどれだけ取れるかを測る (Phase 5 の前処理)。

Phase 3 の `kind` 列 (boy band / girl group / duo/trio / unspecified) だけでは
性別が決まらないケースが多い (実測: 韓国 20% / 日本 en 40%)。
リード文の他の表現をどこまで足せば埋まるかを、段階ごとに測る。

    python3 scripts/probe_sex_signals.py

出力: results/probe_sex_signals.txt
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "results", "probe_sex_signals.txt")

# 段階的に足していく候補シグナル。左が強い順
LAYERS = [
    ("L1 kind 由来", {
        "M": r"\bboy (?:band|group)\b",
        "F": r"\bgirl group\b",
    }),
    ("L2 boy/girl の別表記", {
        "M": r"\bboy (?:band|group)\b|\bboyband\b|\bmale (?:idol )?(?:group|band|duo|trio|vocal group)\b",
        "F": r"\bgirl group\b|\bgirlgroup\b|\bfemale (?:idol )?(?:group|band|duo|trio|vocal group)\b",
    }),
    ("L3 メンバー数表記を追加", {
        "M": (r"\bboy (?:band|group)\b|\bboyband\b|\bmale (?:idol )?(?:group|band|duo|trio|vocal group)\b"
              r"|\b(?:all-)?male\b|\bmen'?s\b"),
        "F": (r"\bgirl group\b|\bgirlgroup\b|\bfemale (?:idol )?(?:group|band|duo|trio|vocal group)\b"
              r"|\b(?:all-)?female\b|\bwomen'?s\b|\ball-girl\b"),
    }),
]

MIXED = r"\bco-ed\b|\bcoed\b|\bmixed[- ]gender\b|\bmixed[- ]sex\b"


def load(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] in out:
                continue
            out[rec["title"]] = rec
    return out


def probe(pages, label, lines):
    a = lines.append
    a(f"## {label} (n={len(pages)})")
    a("")
    leads = {t: re.sub(r"\s+", " ", p.get("lead", "") or "")[:600] for t, p in pages.items()}

    for name, pats in LAYERS:
        res = Counter()
        for t, lead in leads.items():
            m = bool(re.search(MIXED, lead, re.I))
            male = bool(re.search(pats["M"], lead, re.I))
            female = bool(re.search(pats["F"], lead, re.I))
            if m:
                res["mixed"] += 1
            elif male and female:
                res["conflict"] += 1
            elif male:
                res["M"] += 1
            elif female:
                res["F"] += 1
            else:
                res["unknown"] += 1
        total = sum(res.values())
        resolved = total - res["unknown"]
        a(f"- **{name}**: 判明 {resolved}/{total} ({resolved / total:.1%}) "
          f"| M={res['M']} F={res['F']} mixed={res['mixed']} 衝突={res['conflict']} 不明={res['unknown']}")
    a("")

    # 最終層で不明のまま残るものを列挙する。何が漏れているかを目で見て決める
    pats = LAYERS[-1][1]
    unknown = [t for t, lead in leads.items()
               if not re.search(MIXED, lead, re.I)
               and not re.search(pats["M"], lead, re.I)
               and not re.search(pats["F"], lead, re.I)]
    a(f"### 最終層でも不明 {len(unknown)} 件 (先頭 25 件のリード文)")
    a("")
    for t in unknown[:25]:
        a(f"- `{t}`: {leads[t][:150]}")
    a("")

    # 衝突ケースも見る
    conflict = [t for t, lead in leads.items()
                if not re.search(MIXED, lead, re.I)
                and re.search(pats["M"], lead, re.I) and re.search(pats["F"], lead, re.I)]
    a(f"### M/F が衝突 {len(conflict)} 件")
    a("")
    for t in conflict[:15]:
        a(f"- `{t}`: {leads[t][:200]}")
    a("")


def main():
    lines = ["# 英語版 Wikipedia の性別シグナル実測 (Phase 5 前処理)", ""]
    for country in ["kr", "jp"]:
        path = os.path.join(ROOT, "data", "raw", f"en_{country}_pages.jsonl")
        probe(load(path), f"en_{country}_pages", lines)
    text = "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    sys.exit(main())
