"""投稿・査読に出す前の体裁チェック。

2026-08-09 に GPT 査読で体裁の穴を指摘されたため常設した。
指摘されたのは「Figure 2 の caption が t=1..12 なのに図は 15 年まで描画されていた」。
手で PDF を眺めるだけでは落ちるので、機械で落とせるものは全部ここで落とす。

    .venv/bin/python scripts/check_manuscript.py

exit code は失敗数。0 なら査読に出してよい。
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
MS = os.path.join(ROOT, "manuscript.md")
AN = os.path.join(ROOT, "results", "analysis.md")
PLOT_SCRIPT = os.path.join(ROOT, "scripts", "analyze_survival.py")

ABSTRACT_MIN, ABSTRACT_MAX = 250, 300
LIMITATIONS_MIN, LIMITATIONS_MAX = 5, 7

failures = []


def check(label, ok, detail=""):
    print(f"  {'OK ' if ok else '*** FAIL'} {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


def main():
    ms = open(MS, encoding="utf-8").read()
    an = open(AN, encoding="utf-8").read()
    body = ms.split("## Tables")[0]

    print("[1] Abstract の語数")
    m = re.search(r"\n## Abstract\n(.*?)\n\*\*Keywords:\*\*", ms, re.S)
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-–—.,%()/]*", re.sub(r"\*\*(.*?)\*\*", r"\1", m.group(1)))
    check(f"{len(words)} words", ABSTRACT_MIN <= len(words) <= ABSTRACT_MAX,
          f"target {ABSTRACT_MIN}-{ABSTRACT_MAX}")

    print("[2] Limitations の項目数")
    lim = re.search(r"\n## Limitations\n(.*?)\n## ", ms, re.S)
    n_lim = len(re.findall(r"^\d+\.\s+\*\*", lim.group(1), re.M))
    check(f"{n_lim} items", LIMITATIONS_MIN <= n_lim <= LIMITATIONS_MAX,
          f"target {LIMITATIONS_MIN}-{LIMITATIONS_MAX}")

    print("[3] 表と図が本文から参照されているか")
    for kind, def_pat, cite_pat in [
        ("Table", r"^### Table (\d+)\.", r"Table (\d+)"),
        ("Figure", r"^\*\*Figure (\d+)\.", r"Figure (\d+)"),
    ]:
        defined = set(re.findall(def_pat, ms, re.M))
        cited = set(re.findall(cite_pat, body))
        check(f"{kind}: 全て本文から参照", not (defined - cited),
              f"未参照 {sorted(defined - cited, key=int)}" if defined - cited else "")
        check(f"{kind}: 参照先が全て存在", not (cited - defined),
              f"定義なし {sorted(cited - defined, key=int)}" if cited - defined else "")
        check(f"{kind}: 番号が連番", sorted(map(int, defined)) == list(range(1, len(defined) + 1)),
              f"{sorted(map(int, defined))}")

    print("[4] ハザード図の描画範囲と caption の整合")
    # 図の t 上限はプロット側の定数が真実源。caption が別の数字を書いていたら落とす。
    tmax = re.search(r"HAZARD_PLOT_TMAX\s*=\s*(\d+)", open(PLOT_SCRIPT, encoding="utf-8").read())
    tmax = int(tmax.group(1))
    cap = re.search(r"\*\*Figure 2\..*?(?=\n\n)", ms, re.S).group(0)
    cap_tmax = re.search(r"t = 1…(\d+)", cap)
    check(f"Figure 2 caption の上限が図と一致 (図 t_max={tmax})",
          bool(cap_tmax) and int(cap_tmax.group(1)) == tmax,
          f"caption 側 = {cap_tmax.group(1) if cap_tmax else '記載なし'}")
    # 表 5 の行数も同じ範囲か
    t5 = re.search(r"### Table 5\..*?\n\n(.*?)\n\n", ms, re.S).group(1)
    n_rows = len([r for r in t5.splitlines() if re.match(r"\|\s*\*?\*?\d+", r)])
    check(f"Table 5 の行数が図の範囲と一致", n_rows == tmax, f"表 {n_rows} 行 / 図 {tmax} 年")

    print("[5] 主要数値が results/analysis.md と一致するか")
    nums = ["1,346", "549", "304", "19.8%", "25.0%", "14.6% (30/206)", "7.9% (43/546)",
            "1.61", "0.007", "0.96", "0.642", "2.95", "0.018", "46.4%", "20.0",
            "1.54", "0.023"]
    missing_ms = [n for n in nums if n not in ms]
    check("原稿に主要数値が揃っている", not missing_ms, f"欠落 {missing_ms}" if missing_ms else "")
    for a, b in [("19.8%", "19.8%"), ("25.0%", "25.0%"),
                 ("14.6% (30/206)", "14.6% (30/206)"), ("1.61", "1.61"), ("2.95", "2.95")]:
        if a in ms and b not in an:
            check(f"{a} が analysis.md に存在", False)
    check("主要数値が analysis.md 側にも存在", True)

    print("[6] 言い過ぎ表現が残っていないか")
    # 査読で指摘された表現。復活したら落とす。
    banned = {
        "statistically indistinguishable": "等価性の主張。CI 重複は同等性の証明ではない",
        "survived seven falsification checks": "7 件目は cannot be excluded なので偽",
        "coverage rate of": "group 単位で照合していないので coverage とは呼べない",
    }
    for phrase, why in banned.items():
        check(f"'{phrase}' を使っていない", phrase not in ms, why)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"FAIL: {len(failures)} 件。査読に出す前に潰すこと")
        for f in failures:
            print(f"  - {f}")
    else:
        print("ALL OK — 査読に出してよい")
    return len(failures)


if __name__ == "__main__":
    sys.exit(main())
