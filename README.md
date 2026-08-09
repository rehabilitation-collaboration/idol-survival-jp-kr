# Idol Group Survival: A Japan–Korea Comparison

Replication and cross-national extension of a full-census survival analysis of idol groups.

**Status: analysis complete, manuscript drafted, not yet reviewed or submitted.** Both populations are built (Japan n = 1,346 from ja.wikipedia; Korea n = 549 from en.wikipedia), the survival analysis has been run, and a full draft is in `manuscript.md` (build the PDF with `python generate_pdf.py`). Nothing has been peer reviewed and nothing has been submitted, so results here should be treated as a preprint-stage working record rather than as published findings.

## Research question

How long do Japanese idol groups survive in the market, and does the structure differ from Korea?

Kim (2026) analysed a full census of 1,182 K-pop idol groups that debuted between 1996 and 2025, and reported that approximately 45% exit the market within three years of debut — about 42.9% of the standard seven-year exclusive contract period in Korea. Japan has no equivalent standardised contract term. This project asks whether that institutional difference is visible in the shape of the survival curve, in particular whether hazard concentrates around the seven-year mark in Korea but not in Japan.

A second, methodological aim: to test whether a Wikipedia-based census is trustworthy at all, by reconstructing the Korean population with the same method and comparing it against Kim's published figures.

## Method notes

### Identifying idol groups

The population is built from Japanese Wikipedia year-of-formation categories (`YYYY年に結成した音楽グループ`, 1996–2025), not from idol categories. Idol status is then decided by the disjunction of three signals:

| Signal | Description |
|---|---|
| C1 | membership in an idol category |
| C2 | the phrase "アイドル" (idol) in the article's opening definition sentence |
| C3 | the phrase "ダンス&ボーカル" (dance & vocal) in the same sentence |

**Category membership alone is not sufficient.** Measured against a ground-truth set of 64 groups, idol categories alone recover only 51.9% of the core cases, and the failures are structural rather than random: none of the 17 groups from the former Johnny's / STARTO agency and none of the 6 LDH groups appear in any idol category. This reflects an editing convention — these agencies do not describe their acts as "idols" — rather than the composition of the industry. Adding the opening-sentence signals raises recovery to 96.2%.

Agency names are deliberately **not** used for classification. Any hand-curated list of "idol agencies" is arbitrary, and deriving one from category-positive groups is circular, because the categories that would seed it exclude the largest agency entirely.

Groups whose opening sentence names a foreign country without also mentioning Japan are excluded (245 cases, largely Chinese, Taiwanese, British and American acts that appear in the same year-of-formation categories).

### Survival

Three death definitions are implemented (strict / loose / conservative) and reported side by side, because "解散" (disbandment), "活動休止" (suspension of activity) and "無期限活動休止" (indefinite suspension) are distinct events in Japan. Groups without an end date are treated as right-censored.

## Results so far

Full output, including every sensitivity analysis, is in [`results/analysis.md`](results/analysis.md).

The level and the shape disagree. Three-year exit rates are indistinguishable between the two countries, but the hazard functions are not the same shape.

| | Japan (ja.wikipedia, n = 1,346) | Korea (en.wikipedia, n = 549) |
|---|---|---|
| Exit within 3 years | 19.7% (17.7–22.0) | 20.1% (16.9–23.8) |
| Exit within 7 years | 43.5% | 41.6% |
| Hazard at year 7 | 7.9% (43/546) | **9.5% (23/243)** |
| Excess over neighbouring years (5, 6, 8, 9) | ratio 0.96, p = 0.642 | **ratio 1.63, p = 0.016** |

Korea's dissolution hazard rises at year seven — the length of the standard exclusive contract — and falls back immediately afterwards (5.4% at year 6, 9.5% at year 7, 4.4% at year 8). Japan, which has no equivalent contract term, shows no such peak under any of the three death definitions. A discrete-time hazard model with country-specific smooth baselines puts the Korean excess at 2.72 times the Japanese one (95% CI 1.07–6.88, p = 0.035).

Seven falsification checks precede that claim rather than follow it; two alternative explanations survive them and are stated as limitations. See §4.3 of the results file.

On the methodological question: reconstructing the Korean population with this method recovers 549 of Kim's 1,182 groups (46.4%) and a three-year exit rate 24.9 points below the published figure. The gap is reported as a finding about the limits of Wikipedia-based census construction, not hidden.

## Reproduction

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Fetch the population from ja.wikipedia (~35 min, resumable)
python3 scripts/fetch_jp_population.py

# Apply the classification and build the population
.venv/bin/python scripts/build_jp_population.py

# Survival analysis: writes results/analysis.md and plots/
.venv/bin/python scripts/analyze_survival.py

.venv/bin/python -m pytest tests/ -q
```

Scripts under `scripts/probe_*.py` reproduce the measurements that justify each design decision; they are the evidence base for the claims above.

## Repository layout

```
PLAN.md          research plan and design decisions (source of truth)
LITERATURE.md    bibliography, with citation-eligibility status per source
src/             classification logic and survival-analysis components
scripts/         data acquisition, probes, and the analysis driver
tests/           unit tests (179)
results/         analysis.md plus the per-phase measurement reports
plots/           Kaplan-Meier curves and the discrete-time hazard figure
data/            generated datasets (not tracked)
```

## Data and licensing

Group-level data is derived from Japanese, Korean and English Wikipedia via the MediaWiki API. Wikipedia text is licensed **CC BY-SA 4.0**, and derived datasets in this repository inherit that licence. Code is released under the **MIT Licence**.

The source article by Kim (2026) is not redistributed here. Only figures stated in its published English abstract are used.

## Reference

Kim, J-S. (2026). Survival and Hit Structure in the K-pop Idol Music Industry: A Full Census Analysis of 1,182 Groups Debuted Between 1996 and 2025 (Since H.O.T.). *Journal of the Korea Entertainment Industry Association*, 20(4), 71–80. https://doi.org/10.21184/jkeia.2026.7.20.4.71
