"""ヒットデータの構築と、日本側の記事化バイアスの推定 (Phase 4)。

2 つの目的がある:

1. **ヒット構造**: 認定段階別 (ゴールド → プラチナ → ミリオン) にグループ数が
   どう逓減するかを測り、Kim (2026) の winner-take-all 構造と比べる
2. **★ 記事化バイアスの推定**: 「RIAJ 認定があるのに Wikipedia に記事が無い」
   グループを数える。韓国側は Kim (2026) でカバー率 46.4% と分かったが、
   日本側には外部基準が無く、日韓比較の解釈が確定していない

    .venv/bin/python scripts/build_hit_data.py

出力:
    data/jp_certifications.parquet   母集団に紐づいた認定
    results/hit_structure.md         認定段階別の集計と記事化バイアスの推定
"""
import json
import os
import sys
from collections import Counter

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from name_match import build_index, normalize  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
RIAJ = os.path.join(ROOT, "data", "raw", "riaj_gd.jsonl")
POP = os.path.join(ROOT, "data", "jp_groups.parquet")
SURV = os.path.join(ROOT, "data", "jp_survival.parquet")
OUT_PARQUET = os.path.join(ROOT, "data", "jp_certifications.parquet")
OUT_REPORT = os.path.join(ROOT, "results", "hit_structure.md")

# 認定段階の順序 (低い順)。RIAJ の cert 名に対応
CERT_ORDER = [
    "ゴールド", "プラチナ", "ダブル・プラチナ", "トリプル・プラチナ",
    "ミリオン", "2ミリオン", "3ミリオン", "4ミリオン", "5ミリオン",
]

# 名寄せの正解セット。認定を受けていることが自明なグループで精度を測る
GROUND_TRUTH_MATCH = [
    "AKB48", "嵐 (グループ)", "モーニング娘。", "EXILE", "SMAP",
    "乃木坂46", "Kis-My-Ft2", "Hey! Say! JUMP", "SPEED", "Perfume",
]


def load_riaj():
    rows = []
    with open(RIAJ, encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(rows)


def main():
    riaj = load_riaj()
    pop = pd.read_parquet(POP)
    surv = pd.read_parquet(SURV)

    # 日本のアイドルグループが対象なので邦楽に絞る
    jp_riaj = riaj[riaj["hoyo"] == "邦楽"].copy()
    jp_riaj["key"] = jp_riaj["artist"].map(normalize)

    pop_index = build_index(pop["name"])
    pop_keys = set(pop_index)

    jp_riaj["in_population"] = jp_riaj["key"].isin(pop_keys)
    matched = jp_riaj[jp_riaj["in_population"]]

    # 母集団側から見た認定の有無
    pop = pop.copy()
    pop["key"] = pop["name"].map(normalize)
    cert_by_key = matched.groupby("key")
    pop["n_certifications"] = pop["key"].map(cert_by_key.size()).fillna(0).astype(int)
    pop["has_certification"] = pop["n_certifications"] > 0
    top_cert = matched.assign(
        rank=matched["cert"].map({c: i for i, c in enumerate(CERT_ORDER)})
    ).sort_values("rank").groupby("key")["cert"].last()
    pop["top_certification"] = pop["key"].map(top_cert)

    pop[[
        "group_id", "name", "sex", "formed_year", "dissolved_year",
        "has_certification", "n_certifications", "top_certification",
    ]].to_parquet(OUT_PARQUET, index=False)

    write_report(riaj, jp_riaj, matched, pop, surv, pop_index)
    print(f"\n認定紐づけ -> {OUT_PARQUET}")


def write_report(riaj, jp_riaj, matched, pop, surv, pop_index):
    lines = []
    a = lines.append
    a("# ヒット構造と記事化バイアスの推定 (Phase 4)")
    a("")
    a("出典: 日本レコード協会 ゴールドディスク認定 "
      "(`https://www.riaj.or.jp/f/data/api/GdProducts/index.json`・1989 年 4 月以降)")
    a("")
    a("生成: `.venv/bin/python scripts/build_hit_data.py`")
    a("")
    a("## 取得データ")
    a("")
    a(f"- 認定作品 (全体): **{len(riaj):,} 件**")
    a(f"- うち邦楽: **{len(jp_riaj):,} 件**")
    a(f"- 邦楽のユニークアーティスト: **{jp_riaj['artist'].nunique():,} 組/名**")
    a("")

    a("## 名寄せの精度")
    a("")
    a("正解セット (認定があることが自明なグループ) での一致確認:")
    a("")
    a("| グループ | 名寄せ結果 | 認定数 |")
    a("|---|---|---|")
    hit = 0
    for name in GROUND_TRUTH_MATCH:
        k = normalize(name)
        n = int((jp_riaj["key"] == k).sum())
        ok = "✅ 一致" if n else "❌ 未一致"
        hit += bool(n)
        a(f"| {name} | {ok} | {n} |")
    a("")
    a(f"**正解セット {len(GROUND_TRUTH_MATCH)} 件中 {hit} 件が一致 "
      f"({hit / len(GROUND_TRUTH_MATCH):.0%})**")
    a("")

    a("## 母集団の商業的成功")
    a("")
    n_pop = len(pop)
    n_cert = int(pop["has_certification"].sum())
    a(f"- 母集団 {n_pop:,} 組のうち **RIAJ 認定を持つのは {n_cert} 組 "
      f"({n_cert / n_pop:.1%})**")
    a("")
    a("### 認定段階別のグループ数 (winner-take-all 構造)")
    a("")
    a("| 認定段階 | 到達グループ数 | 母集団に占める割合 |")
    a("|---|---|---|")
    for cert in CERT_ORDER:
        keys = set(matched[matched["cert"] == cert]["key"])
        n = int(pop["key"].isin(keys).sum())
        if n == 0 and cert not in ("ゴールド", "プラチナ", "ミリオン"):
            continue
        a(f"| {cert} | {n} | {n / n_pop:.2%} |")
    a("")
    a("Kim (2026) は韓国について「中ヒットから大ヒット・累積メガセラーへ進む")
    a("グループ数が急減する」と報告している (数値はアブストラクトに無い)。")
    a("日本でも同じ逓減構造が出るかを、この表で示す。")
    a("")

    a("## ★ 記事化バイアスの推定")
    a("")
    a("韓国側は Kim (2026) の全数 1,182 組と突き合わせてカバー率 46.4% と分かったが、")
    a("日本側には対応する外部基準が無い。RIAJ 認定を代理基準として使えるかを検討する。")
    a("")
    unmatched = jp_riaj[~jp_riaj["in_population"]]
    a(f"- 邦楽の認定アーティスト {jp_riaj['artist'].nunique():,} 組/名のうち、")
    a(f"  母集団 (アイドルグループ 1,346 組) と一致したのは **{matched['artist'].nunique()} 組**")
    a(f"- 一致しなかったのは {unmatched['artist'].nunique():,} 組/名")
    a("")
    a("### ⚠️ この差はカバー率ではない")
    a("")
    a("一致しない大半は**個人アーティストとバンド**であり、アイドルグループではない。")
    a("RIAJ のデータにアーティスト種別の欄が無いため、")
    a("「認定があるのに記事が無いアイドルグループ」だけを取り出すことはできない。")
    a("")
    a("一致しなかったアーティストの例 (認定数の多い順):")
    a("")
    a("| アーティスト | 認定数 |")
    a("|---|---|")
    for artist, c in Counter(unmatched["artist"]).most_common(15):
        a(f"| {artist} | {c} |")
    a("")
    a("### 結論: RIAJ では日本側のカバー率を測れない")
    a("")
    a("**RIAJ 認定は商業的成功の基準であり、認定を受ける水準のグループは")
    a("ほぼ確実に Wikipedia に記事がある。** 本研究が本当に知りたいのは")
    a("「無名のまま短期間で消えたグループがどれだけ記事化されていないか」だが、")
    a("そうしたグループはそもそも認定を受けない。したがって RIAJ で測れるのは")
    a("**カバー率の上限側 (有名グループはほぼ捕捉できている) の確認に留まる**。")
    a("")
    a("→ 産業全体のカバー率推定には、地下・ライブアイドルまで収録する")
    a("別のレジストリ (idoldb.app 等) との突合が要る。Phase 4 の続きとして実施する。")
    a("")

    a("## 認定と生存の関係 (予備的)")
    a("")
    m = surv.merge(pop[["group_id", "has_certification"]], on="group_id", how="left")
    for flag, label in [(True, "認定あり"), (False, "認定なし")]:
        sub = m[m["has_certification"] == flag]
        dead = sub[sub["death_strict"]]
        a(f"- **{label}** {len(sub):,} 組: 死亡 {len(dead)} 組 "
          f"({len(dead) / max(len(sub), 1):.1%})・"
          f"死亡例の活動年数 中央値 {dead['duration_strict'].median() if len(dead) else float('nan'):.1f} 年")
    a("")
    a("※ 打ち切りを含む生存率の比較は Phase 5 で Kaplan-Meier により行う。")
    a("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
