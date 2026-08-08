"""韓国側の判定シグナルを実測する (Phase 3 の設計根拠)。

英語版 Wikipedia は冒頭定義文の時制で現存と解散を書き分ける傾向がある:

    "2AM is a South Korean boy band ..."      現存
    "100% was a South Korean boy band ..."    解散

日本語版には無いシグナルなので、実際に解散と対応しているかを
独立した 2 ソース (disestablished カテゴリ / Infobox years_active) で検証する。
併せて、母集団に混ざる非アイドル (ロックバンド・プロデューサー集団) の量も測る。

    .venv/bin/python scripts/probe_kr_signals.py
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wikitext import extract_field  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PAGES = os.path.join(ROOT, "data", "raw", "en_kr_pages.jsonl")

YEAR_EST = re.compile(r"^Musical groups established in (\d{4})$")
YEAR_DIS = re.compile(r"^Musical groups disestablished in (\d{4})$")
YEARS_ACTIVE = ["years_active", "Years_active", "years active"]

# 冒頭定義文の主節の時制。読み仮名の括弧を挟むので、最初に現れる be 動詞を採る
TENSE = re.compile(r"\b(is|was|are|were)\b")
# グループ種別
KIND = {
    "boy band": r"\bboy band\b",
    "girl group": r"\bgirl group\b",
    "idol group": r"\bidol group\b",
    "vocal group": r"\bvocal group\b",
    "duo/trio": r"\b(duo|trio)\b",
    "rock/indie band": r"\b(rock band|indie band|alternative rock|punk band|metal band)\b",
    "hip hop group": r"\bhip[- ]hop (group|duo|trio)\b",
    "project/producer": r"\b(producer group|project group)\b",
}


def load():
    out = {}
    with open(PAGES, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("missing") or rec["title"] in out:
                continue
            out[rec["title"]] = rec
    return out


def first_sentence(lead):
    """冒頭の定義文を返す。

    ★ 英語はピリオドを略語にも使うので、最初の '.' で切ると壊れる。
      実例: "BTS (Korean: 방탄소년단; RR: Bangtan sonyeondan; lit." で切れて
      主節 "is a South Korean boy band" に届かず、BTS の種別も時制も
      判定できなかった。ピリオドの後に空白 + 大文字が続く場合のみ文末とみなす。
    """
    s = re.sub(r"\s+", " ", lead or "")
    m = re.search(r"\.\s+(?=[A-Z])", s)
    return (s[: m.start() + 1] if m else s)[:400]


def year_from(cats, pattern):
    ys = [int(m.group(1)) for c in cats if (m := pattern.match(c))]
    return min(ys) if ys else None


def parse_en_years_active(raw):
    """英語版の years_active から終了年を取る。

    '2012–2021' / '2012–present' / '2012-2016, 2019-2021' 等。
    ダッシュの後に年が無ければ現役とみなす (日本語版と同じ考え方)。
    """
    if not raw:
        return None, False
    v = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    v = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", " ", v, flags=re.S)
    v = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", v)
    v = re.sub(r"\{\{[^{}]*\}\}", " ", v)
    if re.search(r"present|current", v, re.I):
        return None, True
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", v)]
    if not years:
        return None, False
    last_pos = v.rfind(str(years[-1])) + 4
    if re.search(r"[-–—]\s*$", v[last_pos:].strip() + " ") or v[last_pos:].strip().startswith("–"):
        return None, True
    return (years[-1], False) if len(years) >= 2 else (None, False)


def main():
    pages = load()
    n = len(pages)
    print(f"取得済み {n} 件\n")

    rows = []
    for title, p in pages.items():
        cats = p["categories"]
        lead1 = first_sentence(p["lead"])
        m = TENSE.search(lead1)
        tense = m.group(1) if m else None
        raw_ya = extract_field(p.get("wikitext", ""), YEARS_ACTIVE)
        ya_end, ya_ongoing = parse_en_years_active(raw_ya)
        rows.append({
            "title": title,
            "est": year_from(cats, YEAR_EST),
            "dis": year_from(cats, YEAR_DIS),
            "tense": tense,
            "past": tense in ("was", "were"),
            "ya_end": ya_end,
            "ya_ongoing": ya_ongoing,
            "has_ya": raw_ya is not None,
            "lead1": lead1,
            "kind": [k for k, pat in KIND.items() if re.search(pat, lead1, re.I)],
        })

    print("--- 冒頭定義文の時制 ---")
    for t, c in Counter(r["tense"] for r in rows).most_common():
        print(f"  {str(t):<8} {c:>4} ({c/n:.1%})")

    past = [r for r in rows if r["past"]]
    pres = [r for r in rows if r["tense"] in ("is", "are")]
    print(f"\n--- 時制 × 解散カテゴリ ---")
    print(f"{'':<22}{'解散cat あり':>12}{'なし':>8}")
    for label, group in [("過去形 (was/were)", past), ("現在形 (is/are)", pres)]:
        d = sum(1 for r in group if r["dis"])
        print(f"  {label:<20}{d:>12}{len(group)-d:>8}")

    print(f"\n--- 時制 × Infobox 終了年 ---")
    print(f"{'':<22}{'終了年 あり':>12}{'なし':>8}")
    for label, group in [("過去形 (was/were)", past), ("現在形 (is/are)", pres)]:
        d = sum(1 for r in group if r["ya_end"])
        print(f"  {label:<20}{d:>12}{len(group)-d:>8}")

    # 3 ソースの重なり
    print("\n--- 死亡シグナル 3 種の重なり ---")
    combo = Counter()
    for r in rows:
        key = "+".join(k for k, v in [
            ("cat", bool(r["dis"])), ("ya", bool(r["ya_end"])), ("past", r["past"])
        ] if v) or "none"
        combo[key] += 1
    for k, c in combo.most_common():
        print(f"  {k:<16} {c:>4}")

    only_past = [r for r in rows if r["past"] and not r["dis"] and not r["ya_end"]]
    print(f"\n--- 過去形だけが死亡を示す例 ({len(only_past)} 件・最大 12 件表示) ---")
    for r in only_past[:12]:
        print(f"  {r['title'][:28]:<30} est={r['est']}  {r['lead1'][:78]}")

    print("\n--- グループ種別 (冒頭定義文) ---")
    kc = Counter()
    for r in rows:
        for k in r["kind"] or ["(該当なし)"]:
            kc[k] += 1
    for k, c in kc.most_common():
        print(f"  {k:<20} {c:>4} ({c/n:.1%})")

    print("\n--- 結成年カテゴリの分布 ---")
    est = [r["est"] for r in rows if r["est"]]
    print(f"  結成年あり: {len(est)}/{n} ({len(est)/n:.1%})")
    print(f"  1996-2025 に収まる: {sum(1 for y in est if 1996 <= y <= 2025)}")
    print(f"  1996 より前: {sum(1 for y in est if y < 1996)} / 2025 より後: {sum(1 for y in est if y > 2025)}")

    no_kind = [r for r in rows if not r["kind"]]
    print(f"\n--- 種別が判定できない例 ({len(no_kind)} 件・最大 10 件) ---")
    for r in no_kind[:10]:
        print(f"  {r['title'][:26]:<28} {r['lead1'][:80]}")


if __name__ == "__main__":
    main()
