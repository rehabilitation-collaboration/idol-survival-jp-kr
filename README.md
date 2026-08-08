# Idol Group Survival: A Japan–Korea Comparison

Replication and cross-national extension of a full-census survival analysis of idol groups.

**Status: work in progress.** The Japanese population has been constructed (n = 1,346). Survival estimation, the Korean population, and the manuscript are not yet done. No results should be cited from this repository at this stage.

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

## Reproduction

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Fetch the population from ja.wikipedia (~35 min, resumable)
python3 scripts/fetch_jp_population.py

# Apply the classification and build the population
.venv/bin/python scripts/build_jp_population.py

.venv/bin/python -m pytest tests/ -q
```

Scripts under `scripts/probe_*.py` reproduce the measurements that justify each design decision; they are the evidence base for the claims above.

## Repository layout

```
PLAN.md          research plan and design decisions (source of truth)
LITERATURE.md    bibliography, with citation-eligibility status per source
src/             classification logic
scripts/         data acquisition and probes
tests/           unit tests for classification and population integrity
results/         summaries and the borderline-case list
data/            generated datasets (not tracked)
```

## Data and licensing

Group-level data is derived from Japanese, Korean and English Wikipedia via the MediaWiki API. Wikipedia text is licensed **CC BY-SA 4.0**, and derived datasets in this repository inherit that licence. Code is released under the **MIT Licence**.

The source article by Kim (2026) is not redistributed here. Only figures stated in its published English abstract are used.

## Reference

Kim, J-S. (2026). Survival and Hit Structure in the K-pop Idol Music Industry: A Full Census Analysis of 1,182 Groups Debuted Between 1996 and 2025 (Since H.O.T.). *Journal of the Korea Entertainment Industry Association*, 20(4), 71–80. https://doi.org/10.21184/jkeia.2026.7.20.4.71
