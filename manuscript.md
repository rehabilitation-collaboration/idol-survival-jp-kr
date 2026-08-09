# Earlier Exit and a Spike at Seven Years: Idol Group Survival in Japan and Korea (1996–2025), with a Discrepancy Analysis Against a Published Korean Census

**Running title:** Korean idol groups exit earlier and cluster at seven years

## Authors

Mizuki Shirai^1^

^1^ Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan

<p style="text-align: left;"><strong>Corresponding author:</strong> Mizuki Shirai, Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan. Email: rehabilitation.collaboration@gmail.com. ORCID: 0009-0005-3615-0670.</p>

---

## Abstract

**Background:** Research on Japanese and Korean idol groups is largely qualitative. Kim (2026) measured Korean idol group survival in a census of 1,182 groups, reporting that about 45% exit within three years of debut; no comparable measurement exists for Japan. They also differ institutionally: Korea has a government-issued standard exclusive contract built on a seven-year benchmark, promulgated in July 2009; Japan has no instrument limiting contract duration.

**Methods:** We built group panels from formation-year categories on Japanese-language Wikipedia (Japan, n = 1,346) and from K-pop categories on English-language Wikipedia (Korea, n = 549), for formations in 1996–2025, censored in 2026. Dissolution-year categories assigned events but never defined cohorts. Idol status came from a coded rule combining categories with the article's opening sentence, calibrated on 64 labelled groups. Survival times are integer years, so we estimated Kaplan–Meier attrition, discrete-time hazards, a binomial excess-hazard test at year seven against pooled neighbouring years, and a complementary log-log model with country-specific baselines.

**Results:** Korean groups exited earlier at every horizon: three-year attrition 25.0% (95% CI 21.5–28.9) against 19.8% (17.7–22.1), and 52.7% against 43.6% by year seven. Timing differed too. Korean hazard peaked at year seven (14.6% against a 9.1% neighbour baseline; ratio 1.61, p = 0.007); Japan showed none (0.96, p = 0.642). The Korean excess was 2.95-fold the Japanese under country-specific baselines (1.21–7.20, p = 0.018). It withstood six of seven falsification checks, survived re-anchoring on activity-start year (1.54, p = 0.023), and appeared only in cohorts formed from 2009. Our Korean panel is 46.4% the size of Kim's census, with a three-year estimate 20.0 points lower.

**Conclusions:** Korean idol groups exited earlier and with a distinct spike at seven years, the latter confined to the industry holding a seven-year contractual benchmark. Incomplete coverage means these are statements about relative timing, not absolute exit rates.

**Keywords:** Survival analysis, discrete-time hazard, idol industry, K-pop, exclusive contracts, cultural industries, Wikipedia as a data source, coverage bias, Japan, South Korea

---

## Introduction

Idol groups — manufactured, agency-developed performing units marketed around sustained fan attachment — are a defining organizational form of the Japanese and Korean popular music industries. Their commercial scale is not marginal. Nagaike (2012) records that the male idol group Arashi generated ¥14.4 billion in CD and DVD sales in 2009 alone, and situates its agency, Johnny & Associates, as a dominant force in Japanese entertainment; Choi and Maliangkay (2014) similarly describe Johnny's Entertainment as the country's controlling male-idol producer since the 1960s. Galbraith and Karlin (2012) document that a single AKB48 release tied to voting rights in the group's 2011 general election sold 1,334,000 copies in one week, a Japanese record.

Despite this scale, the scholarly literature on idols is overwhelmingly interpretive. Galbraith (2012) analyses idols as composites of real and fictional imagery in consumer capitalism; Nagaike (2012) examines female desire in the consumption of male idol images; Oh and Lee (2014) trace how state promotion, shifting occupational aspirations, and television talent formats reinforce one another in Korea. These are studies of meaning, industry structure, and policy, not of duration. They do not tell us how long an idol group lasts.

The quantitative music-economics literature does use survival analysis, but at a different unit of analysis. Strobl and Tucker (2000) study chart success dynamics for albums; Bhattacharjee, Gopal, Lertwachara, Marsden and Telang (2007) model album survival on the Billboard charts and the effect of peer-to-peer file sharing; Giles (2007) analyses time spent at number one on the Hot 100; Im, Song and Jung (2018) extend the approach to songs on digital platforms. In each case the object whose lifetime is measured is a *recording*. The organization that produces the recording — the group — is not the unit at risk.

Kim (2026) closed this gap for Korea. Using a full census of 1,182 idol groups that debuted between 1996 and 2025, Kim reports that approximately 45% exit the market within three years of debut, that this corresponds to about 42.9% of the standard seven-year exclusive contract period, and that the first one to three years constitute the critical window for survival and continued agency investment. Kim's design is explicitly mixed-method, combining statistical analysis, cohort analysis, and expert interviews. To our knowledge — searching OpenAlex and CrossRef, which under-index Japanese- and Korean-language journals — no equivalent full-census measurement has been published for Japan, and no study has compared the *timing* of the exit hazard across the two industries.

The comparison is motivated by a concrete institutional asymmetry, which we verified against primary government sources rather than inferring from our data. On 6 July 2009 the Korea Fair Trade Commission promulgated two standard exclusive contracts for popular-culture artists: a singer-centred form (standard terms No. 10062) and an actor-centred form (No. 10063). In the singer-centred form that governs idol groups, Article 3(2) did *not* cap the term. It provided that where a contract is set to run beyond seven years, the artist may at any time after seven years have elapsed notify the agency of termination, with the contract ending six months after that notice. The actor-centred form instead capped the term outright at seven years (Article 13(1)). Policy responsibility later moved to the Ministry of Culture, Sports and Tourism, and in the current notice (No. 2024-0021, amended 3 June 2024) both forms carry identical cap language: the term may not exceed seven years, extendable only by written agreement. Japan has no counterpart. The Agency for Cultural Affairs guideline on contractual relations in the arts (adopted 27 July 2022, revised 29 October 2024) asks that exclusivity obligations stay within a "reasonably necessary scope" but sets no numeric ceiling, and the Japan Fair Trade Commission's 2018 report on human capital and competition policy treats entertainment exclusivity case by case — noting, in the opposite direction, that a *jointly* agreed upper or lower bound on contract length among multiple engaging firms could suppress competition for talent.

Korea therefore has a bright-line temporal benchmark at seven years and Japan does not (Table 10). If contractual architecture leaves a mark on organizational survival, that mark should appear as a localized feature of the Korean hazard function at t = 7 — a feature distinguishable from any overall difference in how fast groups disappear. We ask three questions. First (**level**), how do Japanese and Korean idol groups compare on cumulative attrition at three, five, seven, and ten years? Second (**timing**), is there an excess exit hazard at exactly seven years, and is it specific to Korea? Third (**method validity**), how does a Wikipedia-derived panel compare with a published census, and in which direction does the resulting bias run? Our answers, in brief: Korean groups exit earlier at every horizon we examine; a hazard spike at seven years is present in Korea, absent in Japan, and robust to six of seven pre-planned falsification checks as well as to re-anchoring the clock on activity-start year; and our Korean panel is 46.4% the size of Kim's census and yields a three-year estimate 20.0 percentage points lower, a discrepancy we treat as a primary finding rather than a footnote.

## Methods

### Study design and reporting

This is a retrospective observational study of organizational survival using publicly available encyclopedic records. Analyses were planned before estimation and recorded in a project plan file preserved in the public repository, including the pre-specification of t = 7 as the focal year and the falsification checks reported below; the study was not registered with an external registry, so we describe these as *planned* rather than *pre-registered*.

### Data sources

Group-level records were retrieved through the MediaWiki API from Japanese-language Wikipedia (`ja.wikipedia.org`) and English-language Wikipedia (`en.wikipedia.org`) on 8 August 2026. Three record types were used: category membership, article wikitext (for infobox fields), and the plain-text lead extract (`prop=extracts&exintro=1&explaintext=1`). Certification data came from the Recording Industry Association of Japan's Gold Disc certification database via its public JSON endpoints (11,372 certification records covering releases from 1989 onward). Institutional documents were downloaded directly from the issuing agencies: the Korea Fair Trade Commission press release of 6 July 2009 with its two annexed standard contracts, the Ministry of Culture, Sports and Tourism notice No. 2024-0021, the Agency for Cultural Affairs guideline, and the Japan Fair Trade Commission's 2018 report.

### Cohort definition, and its separation from event ascertainment

This distinction matters enough to state explicitly, because conflating the two would make inclusion depend on the outcome.

Retrieval took the union of `Category:YYYY年に結成した音楽グループ` and `Category:YYYY年に解散した音楽グループ` for 1996–2025, yielding 7,376 distinct articles. **Cohort membership, however, requires a formation-year category inside the observation window.** A group is admitted only if its formation-year category places it in 1996–2025; a dissolution-year category alone never admits a group. Dissolution categories serve solely to assign death years to groups already in the cohort. All three panels are therefore 100% formation-sourced, which we verified directly (Results, *Cohort membership does not depend on the outcome*).

The residual bias runs opposite to outcome-dependent inclusion: idol groups carrying a dissolution-year category but no formation-year category are *excluded* despite being known to have died — 7 such groups in the Japanese panel, 3 in the Korean, and 3 in the English-language Japanese panel. Dropping known deaths depresses measured attrition rather than inflating it.

We did not use Wikidata. Measured coverage of the relevant properties was 12.7–15.7% for inception (P571) and 0.7–1.3% for dissolution (P576): Japanese Wikipedia records these facts in article text and infoboxes without propagating them to Wikidata, so a SPARQL-based extraction would have discarded almost all dissolution events.

### Idol classification

Assigning idol status is the principal discretionary step, so we calibrated it against a manually labelled ground truth of 64 groups — 52 whose idol status is uncontroversial, plus 12 boundary cases — deliberately arranged by agency so that systematic omission of any single agency's roster would be visible.

Category membership alone performed poorly. It recovered only 51.9% (27/52) of the core set, and the failure was structural rather than random: **all 17 groups from Johnny's/STARTO and all 6 from the LDH family were absent from every idol category**. This is an editorial convention — the very agencies that Nagaike (2012) and Choi and Maliangkay (2014) identify as industry-dominant do not self-describe as "idols," and Wikipedia's category tree mirrors that convention. The article's opening definitional sentence proved closer to industrial reality, recovering 16 of the 17 Johnny's/STARTO groups.

The adopted rule is a disjunction of three inclusion signals:

- **C1** — membership in an idol category (`日本の女性/男性アイドルグループ`, `日本のアイドルグループ`, `アイドルグループ`);
- **C2** — the token アイドル ("idol") in the article's opening definitional sentence;
- **C3** — the tokens ダンス&ボーカル / ダンスボーカル ("dance and vocal") or パフォーマンスグループ in that sentence.

An exclusion rule removes articles whose opening sentence names a foreign country without also referring to Japan. Restricting exclusion to Korea proved insufficient: the per-year categories are worldwide in scope, and Chinese (the SNH48 sister groups), Taiwanese, British, American, and Irish acts remained. The final rule excluded 245 of 1,640 idol-positive articles. We did not require an explicit mention of Japan, because 19.5% of genuinely Japanese groups describe themselves only by locality or agency.

Against the core ground truth, recall was 51.9% for C1 alone, 76.9% for C2 alone, 84.6% for C1∨C2, and **96.2% for C1∨C2∨C3**, which we adopted. Adding "girl group"/"boy group" tokens raised no recall while doubling Korean contamination, and was rejected. Two known misses remain — `MAX (音楽グループ)` and `Little Glee Monster`, described only as a "dance group" and a "vocal group" respectively — which we accept rather than broaden the rule into non-idol territory. Group-type words were not used as exclusions: "band" misfired on TOKIO and 関ジャニ∞, since band-format idol groups exist.

We did not build an agency whitelist. Beyond its arbitrariness, a data-driven version is circular — deriving agency lists from category-positive groups assigns Johnny's an idol rate of zero, since none of its groups carry the category — and infobox agency values are frequently unparseable (`{{Plainlist}}` wrappers) and contaminated by renaming.

### Korean population and source-symmetric layer

Korean-language Wikipedia was unusable for this design: it has 414 idol-group articles and **no per-year formation or dissolution categories at all** (verified for every year 1996–2025, and re-verified after correcting a namespace-prefix bug, since Korean uses `분류:` rather than `Category:`). We therefore built the Korean panel from English-language Wikipedia K-pop categories, intersected with `Musical groups established/disestablished in YYYY`, yielding **n = 549** within the observation window.

This makes the two primary panels source-asymmetric by construction. To bound the consequences, we built a third panel — Japanese groups on English-language Wikipedia (**n = 304**) — giving a layer in which both countries are measured through the same encyclopedia. We report all three throughout and treat neither as definitive.

### Death definitions and censoring

Japanese Wikipedia distinguishes dissolution (解散), hiatus (活動休止), and indefinite hiatus, and these are not interchangeable, so we implemented three definitions rather than collapsing them:

- **conservative** — dissolution-year category only (486 events, 36.1%);
- **strict (primary)** — dissolution-year category *or* an end year in the infobox activity-period field (633 events, 47.0%);
- **loose** — strict plus hiatus statements in the lead with a recoverable year (651 events, 48.4%).

The primary definition is justified by a two-source cross-check: of 1,346 groups, 434 had both signals (years agreeing in 417, or 96.1%), **52 were captured only by the category** (infoboxes left stale), and **146 only by the infobox** (category never applied). Either source alone therefore misses real dissolutions. Formation years agreed in 1,204 of 1,251 doubly sourced cases (96.2%). The Korean panel supports only one definition, closest in content to the Japanese strict definition; the lead-sentence tense convention in English (`is a South Korean boy band` versus `was`) supplements categories and infobox years.

Parsing the infobox activity-period field requires care with templates. Values of the form `{{Start date|2012}}–2021` are common, and stripping templates before reading years leaves ` –2021`, which both loses the start year and reduces the value to a single year — below the two-year threshold our end-year rule requires, so the dissolution is silently dropped. We extract years from `{{start date}}` and `{{end date}}` templates before the generic strip, in both the English and Japanese parsers, with regression tests fixing the behaviour. Correcting this raised Korean deaths from 224 to 285 and Japanese deaths from 632 to 633; all figures reported here are post-correction.

Groups without an end year are right-censored, and all groups are administratively censored in 2026. For Korea, 15 groups are identifiably defunct but without a recoverable year; these are censored, which biases Korean survival upward, and we quantify the effect by exclusion.

### Institutional data

Contract-institution facts were taken only from primary government documents, listed above and archived with retrieval instructions in the repository. Korean documents are distributed in Hangul Word Processor format; we extracted body text by decompressing the `BodyText/Section*` OLE streams and parsing `HWPTAG_PARA_TEXT` records, and we quote the operative clauses verbatim in the reference file. We did not attempt to date the transition of the singer-centred form from a termination right to an outright cap, because we could not obtain the intermediate revision; we therefore report the 2009 and current texts with explicit dates and make no claim about when the change occurred.

### Statistical analysis

Formation and dissolution are recorded at year granularity, so survival time is an integer number of years and a group formed and dissolved in the same year has duration 0. This dictates the estimators.

Cumulative attrition is 1 − S(t) from Kaplan–Meier estimates with 95% confidence intervals, compared by log-rank tests. Hazards are **discrete-time** conditional hazards, h(t) = (deaths in year t) / (risk set at the start of year t).

The focal test asks whether h(7) exceeds what neighbouring years imply. We pool t ∈ {5, 6, 8, 9} to form a baseline rate and compute a one-sided binomial tail probability for the observed deaths at t = 7, reporting the ratio of h(7) to that baseline. This test is transparent about what is being compared but estimates its baseline from adjacent years, making it somewhat anti-conservative. We therefore corroborate it with a model that does not: a complementary log-log discrete-time hazard model on person-period data,

> cloglog h(t) = cubic polynomial in t × country + β · 1{t = 7} × country,

in which the smooth baseline is estimated separately for each country, so a difference in overall curve shape cannot be mistaken for a spike. The cloglog link makes coefficients readable as log hazard ratios.

Cox proportional-hazards models use Efron's method for ties, with all durations shifted by +0.5 years to place events at interval midpoints and avoid zero durations. Model A pools the two countries in the source-symmetric English-language layer with country, sex, and cohort. Model B is Japan-only and adds agency size, defined as the number of same-agency groups within the panel. This avoids importing a hand-built agency list, but it carries a defect we flag rather than defend: the count is taken over the whole 30-year window, so a group formed in 2005 is assigned a size that includes labelmates formed in 2018. Information from after baseline thus enters a baseline covariate, and the measure additionally favours agencies that survived long enough to accumulate rosters. A correct construction would count only same-agency groups existing at the index group's formation. Model B is reported for completeness and its agency-size coefficients should not be read as estimates of an agency-size effect. Proportional hazards were tested with Schoenfeld residuals.

Two further modelling decisions warrant statement. RIAJ certification is **not** used as a covariate: certifications accrue after formation and accumulate with exposure, so conditioning on them induces immortal-time bias. Missing-value indicators (`sex = unknown`, `agency_class = unknown`) are **retained** rather than dropped, because dropping them would systematically remove thin articles and select the panel on notability; their coefficients are consequently uninterpretable and we do not interpret them.

Two further checks address how much the year-seven term owes to modelling choices. First, we refit the Korean discrete-time model with the baseline specified as a polynomial of degree two through five, as a natural cubic spline with four to six degrees of freedom, and as a saturated set of year dummies. Second, because groups sharing a producing agency are not independent, we cluster on agency. English-language K-pop articles carry no `agency` field at all (0 of 641), but 97.1% carry a `label`, and in K-pop the producing agency is usually also the label; we take the first label, normalize away corporate suffixes so that "SM" and "SM Entertainment" resolve to one cluster, and use the result as a cluster identifier for cluster-robust standard errors and for leave-one-cluster-out re-estimation. The label is a proxy for agency and is not interpreted as one.

Analyses used Python 3.14.3 with lifelines 0.30.3, statsmodels 0.14.6, pandas 2.3.3, and matplotlib 3.11.1. The analysis code carries 196 automated tests, including hazard estimates fixed against hand-computable examples, paired checks that a synthetic spike is detected while a spike-free synthetic series is not, and regression tests on the template-parsing defect described above.

### Ethical considerations

This study analyzes publicly available encyclopedic records about organizations and publicly released industry certification data. No individual-level, health, or personally identifying data were accessed, and no human subjects were recruited or contacted. Because the analysis is restricted to already-public records about commercial entities, it does not meet the threshold for human-subjects research under either domestic or international frameworks (e.g., 45 CFR §46.102 for non-human-subjects data); accordingly, no institutional review board approval or waiver was sought or required.

## Results

### Study populations

The primary Japanese panel comprises 1,346 groups with 633 observed dissolutions (47.0%) and a Kaplan–Meier median survival of 9.0 years. The Korean panel comprises 549 groups with 285 dissolutions (51.9%) and a median of 7.0 years. The source-symmetric Japanese panel comprises 304 groups with 138 dissolutions (45.4%) and a median of 13.0 years (Table 1).

Sex was resolved for 94.5% of the Japanese panel (1,108 female, 150 male, 14 mixed) and 95.8% of the Korean panel (235 female, 275 male, 16 mixed). For the English-language panels, sex was derived from categories with lead-sentence text as a secondary source; where both were available they agreed in 99.6% of 460 Korean cases and 99.4% of 181 Japanese cases.

Cohort sizes grow steeply over the window, from 37 Japanese and 28 Korean groups formed in 1996–2000 to 371 and 133 respectively in 2021–2025 (Table 2). The early sparsity is an artifact of encyclopedic coverage rather than industrial history — Kim's census implies a Korean average of roughly 39 debuts per year across the same period — and the most recent cohorts are additionally affected by article-creation lag.

### Cohort membership does not depend on the outcome

Because inclusion criteria that respond to the outcome would inflate hazard estimates, we verified the separation described in the Methods directly. Of 1,379 Japanese articles passing the idol rule, 1,362 carry a formation-year category and 17 do not; the 1,346-group panel consists entirely of groups whose formation-year category falls in the window. The same holds for the English-language panels: 567 of 615 Korean idol-positive articles carry a formation-year category, as do 343 of 433 Japanese ones, and both panels are drawn only from those. No group enters any panel on the strength of a dissolution category.

The asymmetry that remains points the other way. Seven Japanese idol groups carry a dissolution-year category inside the window but no formation-year category, and are therefore excluded although their death is documented; the corresponding counts are 3 for Korea and 3 for the English-language Japanese panel. Losing known deaths biases attrition downward, not upward, and at 0.2–0.5% of panel size the effect is small.

### Attrition level

Korean groups exit earlier than Japanese ones at every horizon we report (Table 3, Figure 1). Three-year attrition is 25.0% (95% CI 21.5–28.9) in Korea against 19.8% (17.7–22.1) in Japan, a gap of 5.2 percentage points whose confidence intervals barely overlap. The separation widens with time: 39.0% versus 33.0% at five years, 52.7% versus 43.6% at seven, and 62.1% versus 53.9% at ten. Median survival is 7.0 years in Korea against 9.0 in Japan. Whole-curve log-rank tests separate the two countries on the source-asymmetric primary pair (χ² = 4.67, p = 0.031) and, more strongly, on the source-symmetric layer (χ² = 20.32, p < 0.001) (Table 4).

The source-symmetric layer inverts the direction — 12.0% three-year attrition for Japan against 25.0% for Korea, a wider gap than the primary comparison — but this is not interpretable as a purer estimate of national difference, because English-language coverage is itself asymmetric: the English panel captures 22.6% of our Japanese panel but 46.4% of Kim's Korean census. Since notability-selected panels skew long-lived, the more thinly covered Japanese side is the more strongly understated. Both comparisons agree on sign, and neither pins down magnitude.

### Discrepancy against Kim (2026)

Two quantities in Kim (2026) can be set beside ours. Our Korean panel contains 549 groups against Kim's 1,182, so it is **46.4% the size of that census**. On three-year exit we estimate 25.0% against Kim's approximately 45%, a **gap of 20.0 percentage points**. Our project plan specified in advance that a discrepancy exceeding 10 percentage points would elevate the limitations of the Wikipedia approach to a primary finding rather than a caveat, and that threshold was crossed.

Two things this comparison is *not*. First, it is not a group-level coverage audit. We did not obtain Kim's roster, so we cannot say which groups are missing, and 46.4% is a ratio of panel sizes rather than a measured capture rate. Second, the populations are not defined on the same clock: Kim counts groups that **debuted** in 1996–2025, whereas ours are groups **formed** in that window. The 20.0-point gap therefore cannot be attributed to encyclopedic under-coverage alone — some unknown part of it is definitional. We report the gap as a discrepancy demanding explanation, not as a quantified coverage rate.

Internal evidence establishes the *direction* of the bias even though its magnitude for Japan is unknown. Splitting the Japanese panel into quartiles of article length, three-year attrition falls monotonically from 36.8% in the shortest quartile (median 4,295 bytes) to 3.0% in the longest (median 57,526 bytes). Groups with any RIAJ certification show 8.7% three-year attrition against 20.7% for the rest. Two independent proxies for prominence thus point the same way: less prominent groups are shorter-lived, so a panel restricted to groups notable enough to have an article systematically understates attrition. That the shortest-article quartile (36.8%) approaches Kim's 45% is consistent with this reading. We stress that article length is a proxy for prominence and cannot exclude reverse causation, in which longer-lived groups accumulate longer articles.

### The seven-year hazard spike

Discrete-time hazards differ in shape as well as level (Table 5, Figure 2). The Japanese hazard rises gradually to a peak of 9.0% at t = 5 and declines thereafter, with t = 7 at 7.9% (43/546) unremarkable relative to its neighbours. The Korean hazard runs at 9–10% through t = 6 (9.3%), jumps to **14.6% at t = 7** (30/206), and falls back to 9.1% at t = 8.

Against a baseline pooled from t ∈ {5, 6, 8, 9}, the Korean hazard at t = 7 is 1.61 times expectation (baseline 9.1%, one-sided p = 0.007). The corresponding Japanese ratio is 0.96 (baseline 8.2%, p = 0.642), and the source-symmetric Japanese ratio is 0.67 (p = 0.901) (Table 6). The spike is present only where the seven-year contractual benchmark exists.

### Falsification checks

Because a single significant test at a single year invites several competing explanations, we planned seven checks (Table 7).

1. **Was t = 7 simply the lucky year?** Repeating the identical test at every year t = 2…12 yields exactly one significant year in Korea — t = 7 — which also carries the largest hazard ratio of the eleven. In Japan no year is significant, and t = 7 ranks ninth of eleven.
2. **Is it a calendar-year shock?** The 30 Korean deaths at t = 7 are spread across dissolution years 2014–2026, the modal year contributing four (13.3%). Deleting that modal year entirely leaves the excess intact (ratio 1.55, p = 0.018).
3. **Is it a parser artifact?** The share of deaths occurring at t = 7 is 11.0% for category-derived years and 9.4% for infobox-derived years, comparable across the two substantial sources; the lead-text source contributes only 3 deaths in total and is too small to compare.
4. **Does it depend on the neighbourhood?** Four alternative baselines give ratios of 1.58–1.65, all with p ≤ 0.008.
5. **Does the Japanese null depend on the death definition?** Ratios are 1.02, 0.96, and 0.93 under conservative, strict, and loose definitions (all non-significant). No definition produces a Japanese spike.
6. **Is it cohort-dependent?** Splitting Korea at 2009 — the year the standard contract was promulgated — the excess is confined to groups formed in 2009–2025 (n = 465; ratio 1.92, p < 0.001) and absent among those formed in 1996–2008 (n = 84; ratio 0.28). The early cohort has only 54 groups in the t = 7 risk set, so this is weak evidence of absence, and we do not treat it as establishing a date of onset.
7. **Could editors be rounding dissolution years toward the contract narrative?** This we cannot exclude, and it is carried into Limitations.

### The formation clock tracks the debut clock

A seven-year contract begins at signature, not at formation, so a spike at seven years since *formation* would be poor evidence for a contract mechanism if the two clocks diverged. They do not. Using the infobox activity-start year as a debut proxy — available for 88.9% of the Korean panel — the activity-start year equals the formation-year category in **96.1%** of cases, with no group starting two or more years later.

Re-anchoring the analysis on activity-start year preserves the result. Within the 488 Korean groups having both clocks, the excess is 1.67 (p = 0.008) on the formation clock and **1.54 (p = 0.023) on the activity-start clock**. Japanese ratios stay near unity on both (0.72 and 0.72). The spike is therefore not an artifact of anchoring at formation.

### Model-based confirmation

The complementary log-log model, fitted to 6,783 person-period rows from the 853 groups of the source-symmetric layer, reproduces the result with country-specific smooth baselines. The interaction of the t = 7 indicator with Korea is +1.082 on the log-hazard scale, a hazard ratio of **2.95 (95% CI 1.21–7.20, p = 0.018)**, while the corresponding Japanese term is 0.58 (0.27–1.28, p = 0.179). Fitted separately, the Korean panel gives 1.72 (1.13–2.64, p = 0.012) and the Japanese primary panel 0.93 (0.67–1.29, p = 0.651) (Table 8). Both the model-free and model-based routes therefore agree.

### The spike does not depend on how the baseline is drawn, or on agency clustering

Because the year-seven term is defined relative to a baseline, its size could in principle be an artifact of the functional form we chose for that baseline. Refitting the Korean model across seven alternative specifications leaves the excess in place: hazard ratios run from 1.58 to 1.97 across polynomials of degree three to five and natural splines with four to six degrees of freedom, all significant at p ≤ 0.043 (Supplementary Table S3). The one exception is a quadratic baseline, which yields 1.41 (p = 0.098) — too rigid to follow the mid-window plateau, so it absorbs part of the spike into the trend.

A saturated year-dummy baseline, which the review suggested as the most flexible option, is not estimable and this is not a numerical accident. If every year receives its own parameter, the indicator for t = 7 coincides exactly with one of those parameters and no "excess" remains to be identified; the model reports a coefficient of astronomical magnitude with an unbounded interval. The point is worth stating plainly: an excess at a particular year is only meaningful relative to a baseline that is assumed smooth, and that assumption is not optional.

Clustering does not overturn the result either. Of the 549 Korean groups, 533 (97.1%) carry a usable label, distributed over 397 clusters with a maximum cluster size of 19 groups. Restricting to those groups leaves the excess essentially unchanged (1.76, p = 0.010), and clustering the standard errors on agency widens the interval only modestly (1.76, 95% CI 1.11–2.79, p = 0.017). Dropping each of the eight largest agencies in turn gives ratios from 1.65 to 1.86, all significant (Supplementary Table S3). No single agency is driving the spike.

### Cox models

In the pooled source-symmetric model (n = 853, 423 events, concordance 0.619), Korea carries a hazard ratio of 1.95 (1.57–2.42, p < 0.001) and male groups 0.55 (0.44–0.68, p < 0.001) relative to female, the latter visible as a separation of the sex-specific curves in both countries (Figure 3); cohort terms are individually non-significant. Schoenfeld residuals reject proportionality for `sex[M]` (χ² = 4.11, p = 0.043), so that coefficient is a period average rather than a constant ratio (Supplementary Table S1).

In the Japan-only model with agency size (n = 1,346, 633 events, concordance 0.568), male groups again show lower hazard (0.63, 0.47–0.84, p = 0.001). The agency-size pattern is **not monotonic**: relative to single-group agencies, agencies with 2–4 groups show a lower hazard (0.79, 0.64–0.99, p = 0.040) while those with 10 or more show a point estimate above one that does not reach significance (1.23, 0.96–1.56, p = 0.102) (Supplementary Table S2). We report this without interpreting it: as noted in the Methods, agency size is counted over the full window and therefore encodes post-baseline information, so these coefficients confound whatever agency size does with the fact that larger counts accrue to agencies that lasted. Proportionality is additionally rejected for `agency_class[unknown]` and for two cohort terms.

### Sensitivity analyses

The direction of the country difference and the seven-year spike are stable across every variation we ran (Table 9). Narrowing the window to 2009–2025 or to 1996–2022 moves Japanese three-year attrition between 19.5% and 20.6% and the Korean between 25.0% and 26.9%; Korea is higher in every window. Dropping the 112 definition-sensitive Japanese groups (8.3% of the panel) shifts Japanese three-year attrition by 0.5 points. Excluding the 15 Korean groups that are defunct without a recoverable year raises Korean three-year attrition from 25.0% to 25.7% and leaves the seven-year excess unchanged (ratio 1.61, p = 0.006).

The death definition moves the Japanese level materially, and this deserves emphasis: Japanese three-year attrition ranges from 14.6% (conservative) through 19.8% (strict) to 20.7% (loose). Because the Korean panel admits only one definition, comparing a conservatively defined Japan against Korea would widen the gap to 10.4 points, roughly double the like-for-like figure. **Cross-country comparison is only meaningful under matched definitions.**

### Certification data, and why no hit structure is reported

Of the 1,346 Japanese groups, 105 (7.8%) hold at least one RIAJ certification. We collected the full certification history intending to report tier-by-tier attainment as a counterpart to the winner-take-most pattern Kim (2026) describes qualitatively for Korea, and we now think that analysis would have been empty. The tiers are nested thresholds on one quantity, so every group at a higher tier is counted at all lower ones and the counts must fall monotonically whatever the underlying distribution; the descending sequence therefore carries no information about concentration. Establishing concentration needs an inequality measure over the certification distribution — a Lorenz curve, a Gini coefficient, or top-percentile shares — which is beyond the scope of a paper about exit timing. The certification records and tier counts are in the repository. We also did not obtain Korean certification data, so no cross-national comparison of hits was possible in any case. Certification is excluded from all models for the immortal-time reason given in the Methods, and enters this paper only as the prominence proxy used above.

## Discussion

### Two findings, not one

Korean idol groups exit earlier than Japanese ones — 25.0% against 19.8% at three years, widening to 52.7% against 43.6% by year seven — and their exit hazard carries a local spike at exactly seven years that has no Japanese counterpart. These are separate claims resting on different evidence, and it is worth keeping them apart. The level difference is a comparison of two panels built from different encyclopedias, and is therefore exposed to every asymmetry in how the two language communities document their idol industries. The timing result is a within-country statement — Korea's year seven against Korea's own neighbouring years — and is immune to that particular objection, which is why we treat it as the more secure of the two.

An earlier version of this analysis reported the two national levels as nearly identical. That reading was an artifact of a template-parsing defect that silently discarded Korean dissolutions recorded as `{{Start date|YYYY}}–YYYY`; correcting it moved Korean deaths from 224 to 285 and Korean three-year attrition from 20.1% to 25.0%. We record this because the corrected figure sits closer to Kim's census value, and because the direction of a measurement error is rarely visible without an external benchmark to check against.

### The institutional reading, and what it cannot establish

The seven-year spike coincides with the only fixed temporal benchmark in either industry, and the mechanism implied by the 2009 text fits what we observe. The singer-centred contract did not terminate relationships at seven years; it gave the artist a *right to exit* once seven years had elapsed. An option creates a spike without emptying the risk set, which is what the data show: hazard at t = 7 rises to 14.6%, not to some far larger value. A hard cap would predict a much more violent depletion.

Two objections that would have been fatal do not hold. The spike is not an artifact of measuring time from formation: Korean formation years coincide with activity-start years in 96.1% of cases, and re-anchoring on the activity-start clock leaves the excess intact (1.54, p = 0.023). Nor does it arise from an inclusion rule that responds to the outcome: cohorts are defined by formation categories alone, and the residual selection drops known deaths rather than adding them.

The cohort split is consistent with the institutional reading — the excess appears among groups formed from 2009 onward and not before — and 2009 is the promulgation year. We are deliberately restrained about this coincidence. The pre-2009 cohort contributes only 54 groups to the relevant risk set, so its null is weak evidence; our design is not a difference-in-differences exploiting the reform; and we cannot observe which contract any individual group actually signed. The alignment is a consistency check, not identification. The termination right also takes effect six months after notice, so the true exit point lies somewhat beyond seven years — a displacement our year-granular clock cannot resolve.

### The coverage shortfall is a finding, not a caveat

Our Korean panel is 46.4% the size of Kim's census and understates three-year exit by 20.0 points. We think this deserves to be reported as a result. Encyclopedic sources are increasingly used as ready-made population frames for cultural industries, and the size of this gap indicates how much can be missed. The internal gradient — three-year attrition falling from 36.8% in the shortest-article quartile to 3.0% in the longest — identifies the mechanism: obscure, short-lived groups are exactly those least likely to be written about.


Does this bias also distort the shape of the hazard, and not only its level? Under-coverage of short-lived groups attenuates measured attrition, and the most obvious version of the mechanism gives no reason for missing groups to have exited disproportionately in their seventh year in Korea specifically. But we cannot rule the possibility out. Whether a group has an article at all, how long that article is, and whether a dissolution year is recorded may each depend on why and when the group ended — and a dissolution that observers can narrate as "the seven-year contract ran out" is exactly the kind that gets written down. That is the same mechanism as the editorial-rounding check we could not close (Table 7, row 7), reappearing at the level of article existence rather than of year assignment.

### Sex differences run opposite to the recording-level literature

Male groups show lower hazard in both countries (0.55 pooled, 0.63 in Japan). This inverts the pattern in the recording-level survival literature, where Bhattacharjee et al. (2007) report enhanced chart survival for female artists and Giles (2007) finds longer stays at number one for female solo performers. The unit of analysis differs — chart tenure of a release versus organizational lifetime of a group — so the two are not in direct contradiction, but the reversal is sharp enough to be worth flagging: what makes a record persist on a chart and what makes a group persist as a going concern are evidently not the same thing.

### Agency size does not act monotonically

Mid-sized agencies (2–4 groups in the panel) show the lowest hazard, while the largest (10+) trend the other way without reaching significance. A simple resources story would not predict that, and Swaminathan's (2001) resource-partitioning account — in which crowding at the market centre creates room for specialists whose advantage depends on maintaining a coherent organizational identity — offers one lens for such non-monotonicity. We raise it only as a direction for future work, because our measure will not carry the weight. Counting same-agency groups across the whole window means a group's covariate is partly determined by events after its own formation, so the variable mixes agency size with agency longevity. Until it is rebuilt as a count at the index group's formation date, the non-monotonicity is a pattern in a mismeasured variable rather than a finding about agencies.

## Limitations

1. **Coverage is incomplete, and the comparison with Kim (2026) is a discrepancy rather than a validation.** Our Korean panel is 46.4% the size of Kim's census and gives a three-year estimate 20.0 percentage points lower, but we did not obtain Kim's roster, so no group-level capture rate was measured. The two frames are also defined differently — Kim counts debuts, we count formations — so an unknown share of the gap is definitional. Only two quantities were comparable at all; mean duration, sex-specific figures, and curve shape were not, and Kim's mixed-method design includes expert interviews that a quantitative replication does not reproduce. For Japan no external benchmark exists, so Japanese coverage is entirely unquantified, and the cross-national level comparison inherits that uncertainty.

2. **Dissolution years may be rounded toward the contract narrative.** If editors record ambiguous endings as coinciding with a well-known seven-year contract term, the spike could be partly an artifact of documentation rather than of behaviour. Our data cannot separate these, and doing so would require records of actual contract expiry dates. The same mechanism could operate on article existence rather than year assignment, which would touch the hazard shape and not only its level.

3. **The clock is coarse.** Survival times are integer years, so same-year events have duration zero and the six-month notice period in the Korean termination right is below resolution. The formation anchor itself is defensible — formation and activity-start years coincide in 96.1% of Korean cases, and the result survives re-anchoring — but sub-annual timing is simply unavailable.

4. **The institutional alignment is not causal identification.** The onset of the excess in post-2009 cohorts matches the promulgation year, but the pre-2009 cohort is small (54 groups at risk at t = 7), no difference-in-differences design was used, and individual groups' contracts are unobserved. We could not date the revision of the singer-centred form from a termination right to an outright cap, so the institutional description rests on two verified time points. Statistically, the neighbour-baseline test estimates its baseline from adjacent years and is anti-conservative, which is why we report the model-based results alongside it; the label-derived cluster variable is a proxy for agency and is missing for 16 groups; and the residual dependence between groups of the *same* agency across *different* labels is not captured by any of our specifications.

5. **Idol classification is validated on recall but not on precision.** The adopted rule recovers 96.2% of a 64-group ground truth, but that ground truth is 52 uncontroversial positives plus 12 boundary cases and contains no sample of clear negatives, so specificity and positive predictive value are unmeasured. The C3 signal in particular ("dance and vocal", "performance group") could admit non-idol acts. Establishing precision would require blind coding of a random sample of candidate articles, which we did not do, and the seven-year result has not been re-estimated under alternative classifier settings. Ground truth was assembled by the author, and 8.3% of the Japanese panel is definition-sensitive — although removing that portion moves three-year attrition by only 0.5 points.

6. **Panel construction differs by country by necessity.** Korean-language Wikipedia has no per-year categories, so the Korean panel is built from English-language Wikipedia while the Japanese primary panel is built from Japanese-language Wikipedia. The source-symmetric layer bounds this but does not remove it, since English-language coverage of the two industries is itself unequal (22.6% of our Japanese panel against 46.4% of Kim's Korean census). Level comparisons between countries should be read with this asymmetry in mind; the seven-year result, being a within-country comparison, is not exposed to it.

7. **The prior literature was verified bibliographically, not read in full.** Citations were checked against OpenAlex and CrossRef and, for nine of eleven works, against retrieved abstracts; none were read in full text. We accordingly cite them for disciplinary positioning rather than as methodological warrants. The search covered OpenAlex and CrossRef, which under-index Japanese- and Korean-language journals, so our claim that no comparable Japanese census exists is a statement about the databases searched.

## Conclusion

Across 1,346 Japanese and 549 Korean idol groups formed between 1996 and 2025, Korean groups exited earlier at every horizon — 25.0% against 19.8% at three years, 52.7% against 43.6% at seven — and their exit hazard carried a spike at seven years that Japan did not show (14.6% against a 9.1% neighbour baseline; ratio 1.61, p = 0.007; 2.95-fold the Japanese excess under country-specific baselines, p = 0.018). The spike withstood six of seven falsification checks, survived re-anchoring the clock from formation to activity-start year, and appeared only among cohorts formed after Korea's standard exclusive contract was promulgated in July 2009 — an alignment we report as consistent with an institutional reading without claiming to have identified it causally. Because cohorts are defined by formation categories alone, the result does not rest on an inclusion rule that responds to the outcome. Set against that, our Korean panel is 46.4% the size of a published census and gives a three-year estimate 20.0 points lower, and the two national panels are drawn from different encyclopedias. The timing result — a within-country comparison — is the firmer of our two findings; the level difference should be read as directional rather than as a measurement of how fast idol groups actually disappear.

## References

1. Kim, J-S. (2026). Survival and Hit Structure in the K-pop Idol Music Industry: A Full Census Analysis of 1,182 Groups Debuted Between 1996 and 2025 (Since H.O.T.). *Journal of the Korea Entertainment Industry Association*, 20(4), 71–80. https://doi.org/10.21184/jkeia.2026.7.20.4.71 (KCI ID ART003366423)

2. Bhattacharjee, S., Gopal, R. D., Lertwachara, K., Marsden, J. R., & Telang, R. (2007). The Effect of Digital Sharing Technologies on Music Markets: A Survival Analysis of Albums on Ranking Charts. *Management Science*, 53(9), 1359–1374. https://doi.org/10.1287/mnsc.1070.0699

3. Giles, D. E. A. (2007). Survival of the hippest: life at the top of the hot 100. *Applied Economics*, 39(15), 1877–1887. https://doi.org/10.1080/00036840600707159

4. Strobl, E. A., & Tucker, C. (2000). The Dynamics of Chart Success in the U.K. Pre-Recorded Popular Music Industry. *Journal of Cultural Economics*, 24(2), 113–134. https://doi.org/10.1023/a:1007601402245

5. Im, H., Song, H., & Jung, J. (2018). A survival analysis of songs on digital music platform. *Telematics and Informatics*, 35(6), 1675–1686. https://doi.org/10.1016/j.tele.2018.04.013

6. Peterson, R. A., & Berger, D. G. (1975). Cycles in Symbol Production: The Case of Popular Music. *American Sociological Review*, 40(2), 158–. https://doi.org/10.2307/2094343 (End page not registered in CrossRef or OpenAlex; start page only.)

7. Swaminathan, A. (2001). Resource Partitioning and the Evolution of Specialist Organizations: The Role of Location and Identity in the U.S. Wine Industry. *Academy of Management Journal*, 44(6), 1169–1185. https://doi.org/10.2307/3069395

8. Galbraith, P. W., & Karlin, J. G. (2012). Introduction: The Mirror of Idols and Celebrity. In *Idols and Celebrity in Japanese Media Culture* (pp. 1–32). Palgrave Macmillan. https://doi.org/10.1057/9781137283788_1

9. Galbraith, P. W. (2012). Idols: The Image of Desire in Japanese Consumer Capitalism. In *Idols and Celebrity in Japanese Media Culture* (pp. 185–208). Palgrave Macmillan. https://doi.org/10.1057/9781137283788_10

10. Nagaike, K. (2012). Johnny's Idols as Icons: Female Desires to Fantasize and Consume Male Idol Images. In *Idols and Celebrity in Japanese Media Culture* (pp. 97–112). Palgrave Macmillan. https://doi.org/10.1057/9781137283788_5

11. Oh, I., & Lee, H. (2014). K-pop in Korea: How the Pop Music Industry Is Changing a Post-Developmental Society. *Cross-Currents: East Asian History and Culture Review*, 3(1), 72–93. https://doi.org/10.1353/ach.2014.0007

12. Choi, J., & Maliangkay, R. (Eds.). (2014). *K-pop: The International Rise of the Korean Music Industry*. Routledge. https://doi.org/10.4324/9781315773568

13. Korea Fair Trade Commission. (2009, July 6). *가수․연기자중심 대중문화예술인 표준전속계약서(2종) 제정* [Establishment of two standard exclusive contracts for popular culture artists, singer-centred and actor-centred]. Standard terms No. 10062 (singer-centred) and No. 10063 (actor-centred). https://www.ftc.go.kr/

14. Ministry of Culture, Sports and Tourism (Republic of Korea). (2024, June 3). *대중문화예술인(가수·연기자) 표준전속계약서* [Standard exclusive contract for popular culture artists (singers and actors)], Notice No. 2024-0021. https://www.mcst.go.kr/

15. Agency for Cultural Affairs (Japan). (2024, October 29 revision; originally adopted 2022, July 27). *文化芸術分野の適正な契約関係構築に向けたガイドライン（検討のまとめ）* [Guideline for building appropriate contractual relationships in the fields of culture and the arts]. https://www.bunka.go.jp/

16. Japan Fair Trade Commission, Competition Policy Research Center. (2018, February 15). *人材と競争政策に関する検討会 報告書* [Report of the study group on human resources and competition policy]. https://www.jftc.go.jp/

17. Recording Industry Association of Japan. (2026). *Gold Disc certifications database*. https://www.riaj.or.jp/data/gd/

## Acknowledgments

The analysis pipeline, statistical code, and manuscript drafting were carried out with assistance from Claude (Anthropic), models Claude Opus 4.6 and Claude Opus 5, used for code generation, data extraction, statistical implementation, and English drafting. All analytical decisions, all interpretation, and the final text are the author's responsibility. All references were verified against OpenAlex and CrossRef for author names, year, venue, and DOI; abstracts were retrieved and read for nine of the eleven scholarly works cited, and full texts were not consulted (see Limitations 7). All institutional documents cited were downloaded from the issuing agencies and their operative clauses read in the original language.

## Author Contributions (CRediT)

Mizuki Shirai: Conceptualization, Methodology, Software, Formal analysis, Data curation, Writing – original draft, Writing – review and editing, Visualization, Project administration.

## Conflict of Interest

The author declares no competing interests, per ICMJE guidelines.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Data Availability

All analysis code, the classification rules, the falsification-check implementations, and the derived result tables are available at https://github.com/rehabilitation-collaboration/idol-survival-jp-kr. Source data are public: Wikipedia content is available under CC BY-SA via the MediaWiki API, and RIAJ certification data via the association's public endpoints. Raw API dumps are excluded from the repository for size, and the retrieval scripts regenerate them. The Korean and Japanese government documents underpinning the institutional description are cited above with retrieval instructions recorded in the repository; the Korean originals are not redistributed because their reuse terms were not verified.

## Tables

### Table 1. Study populations, events, and censoring

| Panel | n | Deaths | Censored | Death rate | Median survival (KM) |
|---|---|---|---|---|---|
| Japan, ja.wikipedia (primary) | 1,346 | 633 | 713 | 47.0% | 9.0 years |
| Korea, en.wikipedia (primary) | 549 | 285 | 264 | 51.9% | 7.0 years |
| Japan, en.wikipedia (symmetric) | 304 | 138 | 166 | 45.4% | 13.0 years |

### Table 2. Cohort sizes by formation period, n (deaths)

| Cohort | Japan | Korea |
|---|---|---|
| 1996–2000 | 37 (27) | 28 (15) |
| 2001–2005 | 51 (33) | 28 (15) |
| 2006–2010 | 122 (73) | 57 (34) |
| 2011–2015 | 349 (206) | 141 (103) |
| 2016–2020 | 416 (217) | 162 (94) |
| 2021–2025 | 371 (77) | 133 (24) |

### Table 3. Cumulative attrition, 1 − S(t), with 95% confidence intervals

| Elapsed years | Japan (primary) | Korea (primary) | Japan (symmetric) |
|---|---|---|---|
| 1 | 6.8% (5.5–8.2) | 7.3% (5.4–9.8) | 3.9% (2.3–6.8) |
| 2 | 13.1% (11.4–15.1) | 16.1% (13.2–19.5) | 7.9% (5.4–11.6) |
| 3 | 19.8% (17.7–22.1) | 25.0% (21.5–28.9) | 12.0% (8.8–16.3) |
| 5 | 33.0% (30.4–35.8) | 39.0% (34.8–43.5) | 23.7% (19.2–29.1) |
| 7 | 43.6% (40.7–46.6) | 52.7% (48.1–57.5) | 30.3% (25.3–36.2) |
| 10 | 53.9% (50.8–57.2) | 62.1% (57.4–66.9) | 40.4% (34.6–46.7) |
| 15 | 62.9% (59.3–66.5) | 65.9% (60.8–70.8) | 54.4% (47.7–61.3) |

### Table 4. Log-rank tests

| Comparison | Panel | χ² | df | p |
|---|---|---|---|---|
| Japan vs Korea (primary; source-asymmetric) | n = 1,895 | 4.67 | 1 | 0.031 |
| Japan vs Korea (symmetric layer) | n = 853 | 20.32 | 1 | < 0.001 |
| Sex (Japan, primary) | n = 1,258 | 6.96 | 1 | 0.008 |
| Sex (Korea, primary) | n = 510 | 13.77 | 1 | < 0.001 |
| Cohort (Japan, primary) | n = 1,346 | 10.26 | 5 | 0.068 |
| Cohort (Korea, primary) | n = 549 | 14.45 | 5 | 0.013 |

Cross-country comparisons use panels built from different encyclopedias; see Limitations 6.

### Table 5. Discrete-time conditional hazards, h(t) = deaths / risk set

| Elapsed years | Japan (primary) | Korea (primary) | Japan (symmetric) |
|---|---|---|---|
| 1 | 6.0% (80/1,335) | 6.6% (36/545) | 3.6% (11/303) |
| 2 | 6.8% (82/1,200) | 9.5% (46/484) | 4.2% (12/289) |
| 3 | 7.7% (82/1,066) | 10.6% (44/416) | 4.4% (12/271) |
| 4 | 8.2% (75/915) | 9.9% (34/342) | 6.1% (15/247) |
| 5 | 9.0% (71/788) | 9.7% (28/288) | 7.7% (17/221) |
| 6 | 8.6% (56/651) | 9.3% (23/248) | 5.0% (10/199) |
| **7** | 7.9% (43/546) | **14.6% (30/206)** | 3.9% (7/181) |
| 8 | 7.7% (35/456) | 9.1% (15/164) | 3.1% (5/160) |
| 9 | 6.7% (26/388) | 7.2% (10/138) | 6.7% (10/150) |
| 10 | 5.2% (17/329) | 5.0% (6/120) | 5.3% (7/131) |
| 11 | 5.5% (15/275) | 3.1% (3/96) | 5.0% (6/119) |
| 12 | 6.8% (15/219) | 2.3% (2/86) | 8.8% (9/102) |

### Table 6. Excess-hazard test at t = 7 against pooled neighbours (t = 5, 6, 8, 9)

| Panel | h(7) | Neighbour baseline | Ratio | p (one-sided) |
|---|---|---|---|---|
| Korea (primary) | 14.6% (30/206) | 9.1% | **1.61** | **0.007** |
| Japan (primary) | 7.9% (43/546) | 8.2% | 0.96 | 0.642 |
| Japan (symmetric) | 3.9% (7/181) | 5.8% | 0.67 | 0.901 |

### Table 7. Falsification checks on the seven-year spike

| # | Alternative explanation | Result |
|---|---|---|
| 1 | t = 7 is the lucky year among many tested | Testing t = 2…12: Korea significant at t = 7 only, and largest ratio of 11; Japan significant nowhere, t = 7 ranks 9th of 11 |
| 2 | A calendar-year dissolution wave | Deaths at t = 7 spread over 2014–2026; deleting the modal year leaves ratio 1.55, p = 0.018 |
| 3 | A single parser's artifact | Share of deaths at t = 7: category 11.0%, infobox 9.4% (lead text contributes only 3 deaths, too few to compare) |
| 4 | Sensitivity to neighbourhood choice | Four alternative baselines give ratios 1.58–1.65, all p ≤ 0.008 |
| 5 | Japanese null depends on death definition | Ratios 1.02 / 0.96 / 0.93 (conservative / strict / loose), none significant |
| 6 | Cohort dependence | 2009–2025 formations: ratio 1.92, p < 0.001 (n = 465). 1996–2008: ratio 0.28 (n = 84; 54 at risk at t = 7, underpowered) |
| 7 | Editorial rounding toward the contract narrative | **Cannot be excluded** — see Limitations 2 |

### Table 8. Complementary log-log discrete-time hazard models

| Specification | Term | Hazard ratio | 95% CI | p |
|---|---|---|---|---|
| Pooled symmetric layer (853 groups, 6,783 person-periods) | t = 7 (Japan, reference country) | 0.58 | 0.27–1.28 | 0.179 |
| Pooled symmetric layer | t = 7 × Korea | **2.95** | 1.21–7.20 | **0.018** |
| Korea (primary), fitted alone | t = 7 | 1.72 | 1.13–2.64 | 0.012 |
| Japan (primary), fitted alone | t = 7 | 0.93 | 0.67–1.29 | 0.651 |

Baseline hazard modelled as a cubic polynomial in t, estimated separately by country.



### Table 9. Sensitivity analyses

| Variation | Japan n | Japan 3-year | Korea n | Korea 3-year | Korea t = 7 ratio (p) |
|---|---|---|---|---|---|
| Primary (1996–2025, strict) | 1,346 | 19.8% | 549 | 25.0% | 1.61 (0.007) |
| Window 2009–2025 | 1,207 | 19.5% | 465 | 26.9% | — |
| Window 1996–2022 | 1,151 | 20.6% | 465 | 26.5% | — |
| Death definition: conservative | 1,346 | 14.6% | — | — | 1.02 (0.473) ‡ |
| Death definition: loose | 1,346 | 20.7% | — | — | 0.93 (0.711) ‡ |
| Definition-sensitive groups removed | 1,234 | 20.3% | — | — | — |
| Korea: year-unknown deaths excluded | — | — | 534 | 25.7% | 1.61 (0.006) |
| Korea: clock re-anchored on activity start | — | — | 488 | — | 1.54 (0.023) |

‡ Japanese ratio under that definition. The Korean panel supports only one death definition.

### Table 10. Contract institutions compared

| | Korea | Japan |
|---|---|---|
| Government-issued standard exclusive contract | Yes (KFTC 2009; MCST current) | No |
| Numeric benchmark on contract term | **Seven years** | None |
| Form of regulation | Ex ante uniform standard | Ex post case-by-case (competition law) |
| Text at promulgation (singer-centred, 2009) | Right to terminate after seven years elapsed, effective six months after notice | — |
| Current text (2024-0021) | Term may not exceed seven years; extension by written agreement | Exclusivity within a "reasonably necessary scope"; no numeric limit |


## Supplementary Materials

The Cox models are subsidiary to the discrete-time analysis, and the robustness grid supports a single sentence in the Results; all three are reported here to keep the main text on the exit-timing argument.

### Supplementary Table S1. Cox model A — pooled, source-symmetric layer (n = 853; 423 events; concordance 0.619)

| Covariate | Hazard ratio | 95% CI | p | Schoenfeld p |
|---|---|---|---|---|
| Country: Korea | 1.95 | 1.57–2.42 | < 0.001 | 0.756 |
| Sex: male | 0.55 | 0.44–0.68 | < 0.001 | **0.043** |
| Sex: mixed | 0.45 | 0.22–0.93 | 0.031 | 0.097 |
| Sex: unknown† | 0.42 | 0.24–0.74 | 0.002 | 0.050 |
| Cohort 2001–2005 | 0.88 | 0.52–1.49 | 0.628 | 0.532 |
| Cohort 2006–2010 | 0.93 | 0.59–1.47 | 0.755 | 0.201 |
| Cohort 2011–2015 | 1.16 | 0.75–1.77 | 0.508 | 0.234 |
| Cohort 2016–2020 | 1.22 | 0.79–1.90 | 0.368 | 0.714 |
| Cohort 2021–2025 | 0.89 | 0.52–1.53 | 0.673 | 0.625 |

References: Japan, female, cohort 1996–2000. † Missingness indicator; not interpreted. Bold marks rejection of proportionality.

### Supplementary Table S2. Cox model B — Japan only, with agency size (n = 1,346; 633 events; concordance 0.568)

| Covariate | Hazard ratio | 95% CI | p | Schoenfeld p |
|---|---|---|---|---|
| Sex: male | 0.63 | 0.47–0.84 | 0.001 | 0.293 |
| Sex: mixed | 1.96 | 1.10–3.52 | 0.023 | 0.536 |
| Sex: unknown† | 0.59 | 0.40–0.87 | 0.008 | 0.705 |
| Agency size 2–4 groups† | 0.79 | 0.64–0.99 | 0.040 | 0.263 |
| Agency size 5–9 groups† | 1.10 | 0.82–1.47 | 0.517 | 0.810 |
| Agency size 10+ groups† | 1.23 | 0.96–1.56 | 0.102 | 0.519 |
| Agency size unknown† | 0.88 | 0.70–1.11 | 0.271 | **< 0.001** |
| Cohort 2001–2005 | 0.89 | 0.53–1.51 | 0.669 | 0.309 |
| Cohort 2006–2010 | 0.77 | 0.48–1.22 | 0.257 | 0.122 |
| Cohort 2011–2015 | 0.88 | 0.57–1.35 | 0.551 | **0.001** |
| Cohort 2016–2020 | 1.15 | 0.75–1.78 | 0.515 | **0.034** |
| Cohort 2021–2025 | 0.97 | 0.60–1.55 | 0.892 | 0.065 |

References: female, single-group agency, cohort 1996–2000. † Not interpreted: missingness indicators, and agency size encodes post-baseline information (see Methods). Bold marks rejection of proportionality.

### Supplementary Table S3. Robustness of the year-seven excess (Korean panel, n = 549)

**Baseline functional form** (all groups; hazard ratio for the t = 7 indicator)

| Baseline | Hazard ratio | 95% CI | p |
|---|---|---|---|
| Quadratic | 1.41 | 0.94–2.11 | 0.098 |
| **Cubic (primary)** | **1.72** | 1.13–2.64 | **0.012** |
| Quartic | 1.97 | 1.26–3.09 | 0.003 |
| Quintic | 1.60 | 1.01–2.52 | 0.043 |
| Natural spline, df = 4 | 1.58 | 1.03–2.41 | 0.036 |
| Natural spline, df = 5 | 1.92 | 1.18–3.13 | 0.009 |
| Natural spline, df = 6 | 1.80 | 1.13–2.86 | 0.014 |
| Saturated year dummies | not identified | — | — |

**Agency clustering** (label-derived clusters; cubic baseline)

| Specification | Hazard ratio | 95% CI | p |
|---|---|---|---|
| All groups, independence assumed (primary) | 1.72 | 1.13–2.64 | 0.012 |
| Groups with a label, independence assumed | 1.76 | 1.15–2.70 | 0.010 |
| Groups with a label, **cluster-robust SE** | 1.76 | 1.11–2.79 | 0.017 |
| Leave-one-cluster-out, 8 largest agencies | 1.65–1.86 | — | 0.008–0.036 |

533 of 549 groups (97.1%) carry a usable label, forming 397 clusters; the largest holds 19 groups.

## Figure Legends

**Figure 1. Kaplan–Meier survival curves.** Two panels. *Left:* primary analysis, using the most complete source for each country (Japan from ja.wikipedia, n = 1,346; Korea from en.wikipedia, n = 549). *Right:* source-symmetric sensitivity analysis, with both countries measured on en.wikipedia (Japan n = 304; Korea n = 549). Shaded bands are 95% confidence intervals and the dashed vertical line marks the seven-year contractual benchmark. Both panels are truncated at 20 years. The Korean curve lies below the Japanese in the left panel from roughly year three onward; in the right panel the gap is wider, reflecting the coverage asymmetry discussed in the text rather than a purer estimate of national difference.

**Figure 2. Discrete-time conditional hazards by year since formation.** Hazard h(t) = deaths in year t divided by the risk set entering year t, plotted for t = 1…12 to match Table 5. Shaded bands are 95% confidence intervals, shown for every series. The Korean series runs at 9–10% through year six, peaks at 14.6% at year seven, and falls back to 9.1% at year eight; the Japanese primary series peaks at year five and declines smoothly, with nothing distinctive at year seven. The pointwise confidence bands are wide relative to the size of the year-seven excess and overlap between series, so this figure should be read together with the formal tests in Tables 6 and 8 rather than on its own.

**Figure 3. Survival by sex.** Kaplan–Meier curves for male and female groups, in two panels. *Left:* Japan, ja.wikipedia (female n = 1,108; male n = 150). *Right:* Korea, en.wikipedia (female n = 235; male n = 275). Shaded bands are 95% confidence intervals. Male groups show longer survival in both countries. Groups coded mixed or unknown are omitted from this figure but retained in all models.

All figure labels are in English.
