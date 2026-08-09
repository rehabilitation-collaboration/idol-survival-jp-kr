# Same Level, Different Shape: A Seven-Year Hazard Concentration in Korean but Not Japanese Idol Groups (1996–2025), with a Wikipedia-Coverage Validation Against a Published Korean Census

**Running title:** Hazard shape, not level, distinguishes Japanese and Korean idol group survival

## Authors

Mizuki Shirai^1^

^1^ Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan

<p style="text-align: left;"><strong>Corresponding author:</strong> Mizuki Shirai, Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan. Email: rehabilitation.collaboration@gmail.com. ORCID: 0009-0005-3615-0670.</p>

---

## Abstract

**Background:** Research on Japanese and Korean idol groups is overwhelmingly qualitative. Kim (2026) measured Korean idol group survival in a full census of 1,182 groups, reporting that approximately 45% exit within three years of debut; no comparable measurement exists for Japan. The industries differ institutionally: Korea has a government-issued standard exclusive contract built on a seven-year benchmark, promulgated by the Korea Fair Trade Commission in July 2009, whereas Japan has no instrument limiting contract duration.

**Methods:** We built group panels from year-of-formation and year-of-dissolution categories on Japanese-language Wikipedia (Japan, n = 1,346) and from K-pop categories on English-language Wikipedia (Korea, n = 549), covering formations in 1996–2025 with administrative censoring in 2026. Idol status came from a coded rule combining category membership with the article's opening definitional sentence, calibrated against 64 labelled groups. Because survival times are integer years, we estimated Kaplan–Meier attrition, discrete-time hazards, a binomial excess-hazard test at year seven against pooled neighbouring years, and a complementary log-log model with country-specific baselines. A Japanese English-language panel (n = 304) supplied a source-symmetric layer.

**Results:** Three-year attrition was statistically indistinguishable (Japan 19.7%, 95% CI 17.7–22.0; Korea 20.1%, 16.9–23.8). Hazard shape was not. Korean hazard rose only at year seven (9.5% against a 5.8% neighbour baseline; ratio 1.63, p = 0.016); Japan showed no excess (7.9% against 8.2%; ratio 0.96, p = 0.642). The Korean excess was 2.72-fold the Japanese (95% CI 1.07–6.88, p = 0.035) and survived seven falsification checks. Against Kim (2026), our Korean panel captured 46.4% of the census and understated three-year attrition by 24.9 percentage points.

**Conclusions:** Attrition level was similar across the two industries while its timing was not, concentration appearing only where a seven-year contractual benchmark exists. The coverage shortfall means these are statements about hazard shape, not about absolute exit rates.

**Keywords:** Survival analysis, discrete-time hazard, idol industry, K-pop, exclusive contracts, cultural industries, Wikipedia as a data source, coverage bias, Japan, South Korea

---

## Introduction

Idol groups — manufactured, agency-developed performing units marketed around sustained fan attachment — are a defining organizational form of the Japanese and Korean popular music industries. Their commercial scale is not marginal. Nagaike (2012) records that the male idol group Arashi generated ¥14.4 billion in CD and DVD sales in 2009 alone, and situates its agency, Johnny & Associates, as a dominant force in Japanese entertainment; Choi and Maliangkay (2014) similarly describe Johnny's Entertainment as the country's controlling male-idol producer since the 1960s. Galbraith and Karlin (2012) document that a single AKB48 release tied to voting rights in the group's 2011 general election sold 1,334,000 copies in one week, a Japanese record.

Despite this scale, the scholarly literature on idols is overwhelmingly interpretive. Galbraith (2012) analyses idols as composites of real and fictional imagery in consumer capitalism; Nagaike (2012) examines female desire in the consumption of male idol images; Oh and Lee (2014) trace how state promotion, shifting occupational aspirations, and television talent formats reinforce one another in Korea. These are studies of meaning, industry structure, and policy, not of duration. They do not tell us how long an idol group lasts.

The quantitative music-economics literature does use survival analysis, but at a different unit of analysis. Strobl and Tucker (2000) study chart success dynamics for albums; Bhattacharjee, Gopal, Lertwachara, Marsden and Telang (2007) model album survival on the Billboard charts and the effect of peer-to-peer file sharing; Giles (2007) analyses time spent at number one on the Hot 100; Im, Song and Jung (2018) extend the approach to songs on digital platforms. In each case the object whose lifetime is measured is a *recording*. The organization that produces the recording — the group — is not the unit at risk.

Kim (2026) closed this gap for Korea. Using a full census of 1,182 idol groups that debuted between 1996 and 2025, Kim reports that approximately 45% exit the market within three years of debut, that this corresponds to about 42.9% of the standard seven-year exclusive contract period, and that the first one to three years constitute the critical window for survival and continued agency investment. Kim's design is explicitly mixed-method, combining statistical analysis, cohort analysis, and expert interviews. To our knowledge — searching OpenAlex and CrossRef, which under-index Japanese- and Korean-language journals — no equivalent full-census measurement has been published for Japan, and no study has compared the *shape* of the exit hazard across the two industries.

The comparison is motivated by a concrete institutional asymmetry, which we verified against primary government sources rather than inferring from our data. On 6 July 2009 the Korea Fair Trade Commission promulgated two standard exclusive contracts for popular-culture artists: a singer-centred form (standard terms No. 10062) and an actor-centred form (No. 10063). In the singer-centred form that governs idol groups, Article 3(2) did *not* cap the term. It provided that where a contract is set to run beyond seven years, the artist may at any time after seven years have elapsed notify the agency of termination, with the contract ending six months after that notice. The actor-centred form instead capped the term outright at seven years (Article 13(1)). Policy responsibility later moved to the Ministry of Culture, Sports and Tourism, and in the current notice (No. 2024-0021, amended 3 June 2024) both forms carry identical cap language: the term may not exceed seven years, extendable only by written agreement. Japan has no counterpart. The Agency for Cultural Affairs guideline on contractual relations in the arts (adopted 27 July 2022, revised 29 October 2024) asks that exclusivity obligations stay within a "reasonably necessary scope" but sets no numeric ceiling, and the Japan Fair Trade Commission's 2018 report on human capital and competition policy treats entertainment exclusivity case by case — noting, in the opposite direction, that a *jointly* agreed upper or lower bound on contract length among multiple engaging firms could suppress competition for talent.

Korea therefore has a bright-line temporal benchmark at seven years and Japan does not. If contractual architecture leaves a mark on organizational survival, that mark should appear as a localized feature of the Korean hazard function at t = 7, not as a difference in overall attrition. We ask three questions. First (**level**), how do Japanese and Korean idol groups compare on cumulative attrition at three, five, seven, and ten years? Second (**shape**), is there an excess exit hazard at exactly seven years, and is it specific to Korea? Third (**method validity**), how much of the Korean industry does a Wikipedia-derived panel actually capture, and in which direction does the resulting bias run? Our answers, in brief: attrition level is statistically indistinguishable between the two countries; hazard concentration at seven years is present in Korea and absent in Japan, and survives seven pre-planned falsification checks; and our Korean panel captures 46.4% of Kim's census while understating three-year attrition by 24.9 percentage points, a shortfall we treat as a primary finding rather than a footnote.

## Methods

### Study design and reporting

This is a retrospective observational study of organizational survival using publicly available encyclopedic records. Analyses were planned before estimation and recorded in a project plan file preserved in the public repository, including the pre-specification of t = 7 as the focal year and the falsification checks reported below; the study was not registered with an external registry, so we describe these as *planned* rather than *pre-registered*.

### Data sources

Group-level records were retrieved through the MediaWiki API from Japanese-language Wikipedia (`ja.wikipedia.org`) and English-language Wikipedia (`en.wikipedia.org`) on 8 August 2026. Three record types were used: category membership, article wikitext (for infobox fields), and the plain-text lead extract (`prop=extracts&exintro=1&explaintext=1`). Certification data for the Japanese hit-structure analysis came from the Recording Industry Association of Japan's Gold Disc certification database via its public JSON endpoints (11,372 certification records covering releases from 1989 onward). Institutional documents were downloaded directly from the issuing agencies: the Korea Fair Trade Commission press release of 6 July 2009 with its two annexed standard contracts, the Ministry of Culture, Sports and Tourism notice No. 2024-0021, the Agency for Cultural Affairs guideline, and the Japan Fair Trade Commission's 2018 report.

### Japanese population

Japanese-language Wikipedia maintains per-year categories for musical groups formed and dissolved in a given year. Taking the union of `Category:YYYY年に結成した音楽グループ` and `Category:YYYY年に解散した音楽グループ` for 1996–2025 yielded 7,376 distinct articles, from which idol groups were identified by the classification rule below, producing the primary Japanese panel of **n = 1,346**.

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
- **strict (primary)** — dissolution-year category *or* an end year in the infobox activity-period field (632 events, 47.0%);
- **loose** — strict plus hiatus statements in the lead with a recoverable year (650 events, 48.3%).

The primary definition is justified by a two-source cross-check: of 1,346 groups, 434 had both signals (years agreeing in 417, or 96.1%), **52 were captured only by the category** (infoboxes left stale), and **146 only by the infobox** (category never applied). Either source alone therefore misses real dissolutions. Formation years agreed in 1,204 of 1,251 doubly sourced cases (96.2%). The Korean panel supports only one definition, closest in content to the Japanese strict definition; the lead-sentence tense convention in English (`is a South Korean boy band` versus `was`) supplied 112 of its death years, alongside 154 from categories and 101 from infoboxes.

Groups without an end year are right-censored, and all groups are administratively censored in 2026. For Korea, 46 groups (8.4%) are identifiably defunct but without a recoverable year; these are censored, which biases Korean survival upward, and we quantify the effect by exclusion.

### Institutional data

Contract-institution facts were taken only from primary government documents, listed above and archived with retrieval instructions in the repository. Korean documents are distributed in Hangul Word Processor format; we extracted body text by decompressing the `BodyText/Section*` OLE streams and parsing `HWPTAG_PARA_TEXT` records, and we quote the operative clauses verbatim in the reference file. We did not attempt to date the transition of the singer-centred form from a termination right to an outright cap, because we could not obtain the intermediate revision; we therefore report the 2009 and current texts with explicit dates and make no claim about when the change occurred.

### Statistical analysis

Formation and dissolution are recorded at year granularity, so survival time is an integer number of years and a group formed and dissolved in the same year has duration 0. This dictates the estimators.

Cumulative attrition is 1 − S(t) from Kaplan–Meier estimates with 95% confidence intervals, compared by log-rank tests. Hazards are **discrete-time** conditional hazards, h(t) = (deaths in year t) / (risk set at the start of year t).

The focal test asks whether h(7) exceeds what neighbouring years imply. We pool t ∈ {5, 6, 8, 9} to form a baseline rate and compute a one-sided binomial tail probability for the observed deaths at t = 7, reporting the ratio of h(7) to that baseline. This test is transparent about what is being compared but estimates its baseline from adjacent years, making it somewhat anti-conservative. We therefore corroborate it with a model that does not: a complementary log-log discrete-time hazard model on person-period data,

> cloglog h(t) = cubic polynomial in t × country + β · 1{t = 7} × country,

in which the smooth baseline is estimated separately for each country, so a difference in overall curve shape cannot be mistaken for a spike. The cloglog link makes coefficients readable as log hazard ratios.

Cox proportional-hazards models use Efron's method for ties, with all durations shifted by +0.5 years to place events at interval midpoints and avoid zero durations. Model A pools the two countries in the source-symmetric English-language layer with country, sex, and cohort. Model B is Japan-only and adds agency size, defined as the number of same-agency groups within the panel — a deliberately crude proxy that avoids importing a hand-built agency list, but which accumulates over the 30-year window and so favours long-lived agencies. Proportional hazards were tested with Schoenfeld residuals.

Two modelling decisions warrant statement. First, RIAJ certification is **not** used as a covariate: certifications accrue after formation and accumulate with exposure, so conditioning on them induces immortal-time bias. We report certification descriptively only. Second, missing-value indicators (`sex = unknown`, `agency_class = unknown`) are **retained** rather than dropped, because dropping them would systematically remove thin articles and select the panel on notability; their coefficients are consequently uninterpretable and we do not interpret them.

Analyses used Python 3.14.3 with lifelines 0.30.3, statsmodels 0.14.6, pandas 2.3.3, and matplotlib 3.11.1. The analysis code carries 179 automated tests, including hazard estimates fixed against hand-computable examples and paired checks that a synthetic spike is detected while a spike-free synthetic series is not.

### Ethical considerations

This study analyzes publicly available encyclopedic records about organizations and publicly released industry certification data. No individual-level, health, or personally identifying data were accessed, and no human subjects were recruited or contacted. Because the analysis is restricted to already-public records about commercial entities, it does not meet the threshold for human-subjects research under either domestic or international frameworks (e.g., 45 CFR §46.102 for non-human-subjects data); accordingly, no institutional review board approval or waiver was sought or required.

## Results

### Study populations

The primary Japanese panel comprises 1,346 groups with 632 observed dissolutions (47.0%) and a Kaplan–Meier median survival of 9.0 years. The Korean panel comprises 549 groups with 224 dissolutions (40.8%) and a median of 12.0 years. The source-symmetric Japanese panel comprises 304 groups with 125 dissolutions (41.1%) and a median of 17.0 years (Table 1).

Sex was resolved for 94.5% of the Japanese panel (1,108 female, 150 male, 14 mixed) and 95.8% of the Korean panel (235 female, 275 male, 16 mixed). For the English-language panels, sex was derived from categories with lead-sentence text as a secondary source; where both were available they agreed in 99.6% of 460 Korean cases and 99.4% of 181 Japanese cases.

Cohort sizes grow steeply over the window, from 37 Japanese and 28 Korean groups formed in 1996–2000 to 371 and 133 respectively in 2021–2025 (Table 2). The early sparsity is an artifact of encyclopedic coverage rather than industrial history — Kim's census implies a Korean average of roughly 39 debuts per year across the same period — and the most recent cohorts are additionally affected by article-creation lag.

### Attrition level

Cumulative attrition is close to identical between the two primary panels at every horizon we report through ten years (Table 3). Three-year attrition is 19.7% (95% CI 17.7–22.0) in Japan and 20.1% (16.9–23.8) in Korea, a difference of 0.4 percentage points with heavily overlapping intervals. Five-year attrition is 33.0% versus 31.8%, seven-year 43.5% versus 41.6%, and ten-year 53.9% versus 48.4%. The curves separate only in the far tail, where the Japanese figure reaches 62.9% at fifteen years against the Korean 51.5%.

The source-symmetric layer tells a different story — 12.0% three-year attrition for Japan against 20.1% for Korea — but this comparison is not interpretable as a national difference, because English-language coverage is itself asymmetric: the English panel captures 22.6% of our Japanese panel but 46.4% of Kim's Korean census. Since notability-selected panels skew long-lived, the more thinly covered Japanese side is the more strongly understated. A log-rank test on this layer returns p = 0.040, and on the source-asymmetric primary pair p = 0.016; we regard neither as evidence about national difference (Table 4).

### Coverage validation against Kim (2026)

Two quantities in Kim (2026) are comparable to ours. On population size, our Korean panel contains 549 groups against Kim's 1,182 — a **coverage rate of 46.4%**. On three-year exit, we estimate 20.1% against Kim's approximately 45% — an **understatement of 24.9 percentage points**. Our project plan specified in advance that a discrepancy exceeding 10 percentage points would elevate the limitations of the Wikipedia approach to a primary finding rather than a caveat, and that threshold was crossed.

Internal evidence establishes the *direction* of the bias even though its magnitude for Japan is unknown. Splitting the Japanese panel into quartiles of article length, three-year attrition falls monotonically from 36.8% in the shortest quartile (median 4,295 bytes) to 3.0% in the longest (median 57,526 bytes). Groups with any RIAJ certification show 8.7% three-year attrition against 20.7% for the rest. Two independent proxies for prominence thus point the same way: less prominent groups are shorter-lived, so a panel restricted to groups notable enough to have an article systematically understates attrition. That the shortest-article quartile (36.8%) approaches Kim's 45% is consistent with this reading. We stress that article length is a proxy for prominence and cannot exclude reverse causation, in which longer-lived groups accumulate longer articles; this is evidence on direction, not an estimate of coverage.

### The seven-year hazard concentration

Discrete-time hazards diverge in shape (Table 5, Figure 2). The Japanese hazard rises gradually to a peak of 9.0% at t = 5 and declines thereafter, with t = 7 at 7.9% (43/546) entirely unremarkable relative to its neighbours. The Korean hazard runs at or below the Japanese level through t = 6 (5.4%), jumps to **9.5% at t = 7** (23/243), and falls to 4.4% at t = 8.

Against a baseline pooled from t ∈ {5, 6, 8, 9}, the Korean hazard at t = 7 is 1.63 times expectation (baseline 5.8%, one-sided p = 0.016). The corresponding Japanese ratio is 0.96 (baseline 8.2%, p = 0.642), and the source-symmetric Japanese ratio is 0.76 (p = 0.821) (Table 6). The excess is present only where the seven-year contractual benchmark exists.

### Falsification checks

Because a single significant test at a single year invites several competing explanations, we planned seven checks (Table 7).

1. **Was t = 7 simply the lucky year?** Repeating the identical test at every year t = 2…12 yields exactly one significant year in Korea — t = 7 — which also carries the largest hazard ratio of the eleven. In Japan no year is significant, and t = 7 ranks ninth of eleven.
2. **Is it a calendar-year shock?** The 23 Korean deaths at t = 7 are spread across dissolution years 2014–2026, the modal year contributing three (13.0%). Deleting that modal year entirely leaves the excess intact (ratio 1.53, p = 0.041).
3. **Is it a parser artifact?** The share of deaths occurring at t = 7 is 11.0% for category-derived years, 7.5% for infobox-derived years, and 11.8% for lead-derived years — comparable across all three sources.
4. **Does it depend on the neighbourhood?** Four alternative baselines give ratios of 1.48–1.90, all with p < 0.05.
5. **Does the Japanese null depend on the death definition?** Ratios are 1.02, 0.96, and 0.93 under conservative, strict, and loose definitions (all non-significant). No definition produces a Japanese spike.
6. **Is it cohort-dependent?** Splitting Korea at 2009 — the year the standard contract was promulgated — the excess is confined to groups formed in 2009–2025 (n = 465; ratio 2.09, p < 0.001) and absent among those formed in 1996–2008 (n = 84; ratio 0.28). The early cohort has only 54 groups in the t = 7 risk set, so this is weak evidence of absence, and we do not treat it as establishing a date of onset.
7. **Could editors be rounding dissolution years toward the contract narrative?** This we cannot exclude, and it is carried into Limitations.

### Model-based confirmation

The complementary log-log model, fitted to 7,199 person-period rows from the 853 groups of the source-symmetric layer, reproduces the result with country-specific smooth baselines. The interaction of the t = 7 indicator with Korea is +1.000 on the log-hazard scale, a hazard ratio of **2.72 (95% CI 1.07–6.88, p = 0.035)**, while the corresponding Japanese term is 0.65 (0.30–1.44, p = 0.291). Fitted separately, the Korean panel gives 1.78 (1.09–2.90, p = 0.021) and the Japanese primary panel 0.93 (0.67–1.29, p = 0.650) (Table 8). Both the model-free and model-based routes therefore agree.

### Cox models

In the pooled source-symmetric model (n = 853, 349 events, concordance 0.597), Korea carries a hazard ratio of 1.55 (1.23–1.96, p < 0.001) and male groups 0.50 (0.40–0.64, p < 0.001) relative to female; cohort terms are individually non-significant. Schoenfeld residuals do not reject proportionality for any covariate (Table 9).

In the Japan-only model with agency size (n = 1,346, 632 events, concordance 0.570), male groups again show lower hazard (0.62, 0.47–0.83, p = 0.001). Agency size is **not monotonic**: relative to single-group agencies, agencies with 2–4 groups show a lower hazard (0.79, 0.63–0.98, p = 0.033) while those with 10 or more show a point estimate above one that does not reach significance (1.23, 0.96–1.57, p = 0.099), and the 5–9 band sits between at 1.10 (Table 10). Here proportionality is rejected for `agency_class[unknown]` and for two cohort terms, so these hazard ratios should be read as period-averaged; the time-resolved structure is the discrete-time hazard reported above.

### Sensitivity analyses

Conclusions are stable across every variation we ran (Table 11). Narrowing the window to 2009–2025 or to 1996–2022 moves Japanese three-year attrition between 19.4% and 20.6% and the Korean between 20.1% and 21.3%. Dropping the 112 definition-sensitive Japanese groups (8.3% of the panel) shifts three-year attrition by 0.5 points. Excluding the 46 Korean groups that are defunct without a recoverable year raises Korean three-year attrition from 20.1% to 22.0% and leaves the seven-year excess essentially unchanged (ratio 1.64, p = 0.014).

The death definition does move the level materially, and this deserves emphasis: Japanese three-year attrition ranges from 14.6% (conservative) through 19.7% (strict) to 20.6% (loose). Because the Korean panel admits only one definition, comparing a conservatively defined Japan against Korea would manufacture a 5.5-point gap where the like-for-like comparison shows none. **Cross-country comparison is only meaningful under matched definitions.**

### Hit structure (Japan)

Of the 1,346 Japanese groups, 105 (7.8%) hold any RIAJ certification. Attainment thins sharply with each tier: 94 groups reach Gold (6.98% of the panel), 44 Platinum (3.27%), 26 Double Platinum, 17 Triple Platinum, 14 Million (1.04%), 4 Double Million, and 1 Triple Million (Table 12). This reproduces in Japan the winner-take-most thinning that Kim (2026) describes qualitatively for Korea. We did not obtain Korean certification data, so this is a within-Japan description and not a cross-national comparison.

## Discussion

### Level and shape are separate questions

The headline result is a dissociation. On the question the existing literature poses — what fraction of groups exit early — Japan and Korea are indistinguishable, with three-year attrition of 19.7% and 20.1% and confidence intervals that overlap almost entirely. Had we stopped there, the natural conclusion would have been that two industries with visibly different contractual and developmental regimes nonetheless produce the same survival outcome.

The hazard function tells a different story. Korea's exit risk is flat-to-declining through year six, spikes at year seven, and falls again; Japan's is a smooth hump peaking at year five with nothing distinctive at seven. Aggregate attrition curves hide this because a single-year excess of a few percentage points contributes little to a cumulative total. The practical implication is methodological: in industries organized around contractual periods, the timing of exit may carry information that the level does not.

### The institutional reading, and what it cannot establish

The seven-year concentration coincides with the only fixed temporal benchmark in either industry, and the mechanism implied by the 2009 text is a good fit for what we observe. The singer-centred contract did not terminate relationships at seven years; it gave the artist a *right to exit* once seven years had elapsed. An option creates a spike without emptying the risk set, which is what the data show: hazard at t = 7 rises to 9.5%, not to some far larger value. A hard cap would predict a much more violent depletion.

The cohort split is consistent with this reading — the excess appears among groups formed from 2009 onward and not before — and 2009 is the promulgation year. We are deliberately restrained about this coincidence. The pre-2009 cohort contributes only 54 groups to the relevant risk set, so its null is weak evidence; our design is not a difference-in-differences exploiting the reform; and we cannot observe which contract any individual group actually signed. The alignment is a consistency check, not identification.

Two further cautions belong here. The termination right takes effect six months after notice, so the true exit point lies somewhat beyond seven years — a displacement our year-granular, formation-anchored clock cannot resolve. And the clock itself starts at formation, not at contract signature or debut; trainee periods of one to two years are absorbed invisibly.

### The coverage shortfall is a finding, not a caveat

Our Korean panel recovers 46.4% of Kim's census and understates three-year exit by 24.9 percentage points. We think this deserves to be reported as a result. Encyclopedic sources are increasingly used as ready-made population frames for cultural industries, and the size of this gap indicates how much can be missed. The internal gradient — three-year attrition falling from 36.8% in the shortest-article quartile to 3.0% in the longest — identifies the mechanism: obscure, short-lived groups are exactly those least likely to be written about.

There is an irony worth recording. We evaluated several commercial talent databases and rejected them for this purpose. One directory covering 2,981 groups carried dissolution information for only 88 of them (3%); paid casting databases are screen-only and do not document whether defunct groups are retained. Commercial catalogues exist to market currently active talent, so they have no incentive to preserve the dead. For measuring organizational mortality, the volunteer encyclopedia is the more complete record — while still, as our own validation shows, missing more than half the population.

Crucially, the direction of this bias cannot explain away our central result. Under-coverage of short-lived groups attenuates measured attrition levels; it provides no reason for the missing groups to have exited disproportionately in their seventh year in Korea and not in Japan.

### Sex differences run opposite to the recording-level literature

Male groups show lower hazard in both countries (0.50 pooled, 0.62 in Japan). This inverts the pattern in the recording-level survival literature, where Bhattacharjee et al. (2007) report enhanced chart survival for female artists and Giles (2007) finds longer stays at number one for female solo performers. The unit of analysis differs — chart tenure of a release versus organizational lifetime of a group — so the two are not in direct contradiction, but the reversal is sharp enough to be worth flagging: what makes a record persist on a chart and what makes a group persist as a going concern are evidently not the same thing.

### Agency size does not act monotonically

Mid-sized agencies (2–4 groups in the panel) show the lowest hazard, while the largest (10+) trend the other way without reaching significance. This is not what a simple resources story predicts. Swaminathan's (2001) resource-partitioning account, in which crowding at the market centre creates room for specialists whose advantage depends on maintaining a coherent organizational identity, offers one lens for such non-monotonicity, though testing it would require agency-level data we do not have. Our measure is in any case crude — a count of same-agency groups within the panel, accumulated over thirty years — and we would not want it read as an estimate of agency capability.

## Limitations

1. **Coverage is incomplete and its magnitude is known only for Korea.** Our Korean panel captures 46.4% of Kim's census and understates three-year attrition by 24.9 percentage points. For Japan no external benchmark exists, so Japanese coverage remains unquantified. All attrition levels reported here should be read as lower bounds, and the internal quartile gradient (36.8% to 3.0%) indicates the bias direction without estimating its size. Reverse causation — longer-lived groups accumulating longer articles — cannot be excluded.

2. **Only two quantities could be validated against Kim (2026).** We did not obtain the full text, so comparison is limited to population size and three-year exit. Mean duration, sex-specific figures, and curve shape are not comparable, and Kim's mixed-method design includes expert interviews that a purely quantitative replication does not reproduce. Agreement on two points does not validate the method as a whole.

3. **Dissolution years may be rounded toward the contract narrative.** If editors record ambiguous endings as coinciding with a well-known seven-year contract term, the spike could be partly an artifact of documentation rather than of behaviour. Our data cannot separate these, and doing so would require records of actual contract expiry dates.

4. **The clock is coarse and anchored at formation.** Survival times are integer years derived from formation and dissolution years, so same-year events have duration zero and the six-month notice period in the Korean termination right is below resolution. Formation is not contract signature and not debut; trainee periods of one to two years are unmodelled.

5. **The institutional alignment is not causal identification.** The onset of the excess in post-2009 cohorts matches the promulgation year, but the pre-2009 cohort is small (54 groups at risk at t = 7), no difference-in-differences design was used, and individual groups' contracts are unobserved. We also could not date the revision of the singer-centred form from a termination right to an outright cap, so the institutional description is anchored to two verified time points rather than a continuous history.

6. **Idol classification is rule-based and imperfect.** The adopted rule recovers 96.2% of a 64-group ground truth, leaving two known misses that we accept deliberately. Ground truth was assembled by the author, the boundary between idol and adjacent formats is genuinely contested, and 8.3% of the Japanese panel is definition-sensitive — although removing that portion moves three-year attrition by only 0.5 points. Panel construction also differs by country by necessity, since Korean-language Wikipedia has no per-year categories.

7. **The prior literature was verified bibliographically, not read in full.** Citations were checked against OpenAlex and CrossRef and, for nine of eleven works, against retrieved abstracts; none were read in full text. We accordingly cite them for disciplinary positioning rather than as methodological warrants. The search covered OpenAlex and CrossRef, which under-index Japanese- and Korean-language journals, so our claim that no comparable Japanese census exists is a statement about the databases searched.

## Conclusion

Across 1,346 Japanese and 549 Korean idol groups formed between 1996 and 2025, cumulative attrition was statistically indistinguishable between the two industries — 19.7% versus 20.1% at three years, with overlapping confidence intervals — while the timing of exit was not. Korean exit hazard was concentrated at exactly seven years (9.5% against a 5.8% neighbour baseline; ratio 1.63, p = 0.016; 2.72-fold the Japanese excess in a model with country-specific baselines, p = 0.035), whereas Japan showed no such feature under any death definition. The concentration appears only in the industry that has a seven-year contractual benchmark, and only among cohorts formed after that benchmark was promulgated in July 2009 — an alignment we report as consistent with an institutional reading without claiming to have identified it causally. Separately, validating our Korean panel against a published census showed that it captures 46.4% of the population and understates three-year attrition by 24.9 percentage points, which sets the terms on which these results should be used: as evidence about the shape of the exit hazard, not about the absolute rate at which idol groups disappear.

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
| Japan, ja.wikipedia (primary) | 1,346 | 632 | 714 | 47.0% | 9.0 years |
| Korea, en.wikipedia (primary) | 549 | 224 | 325 | 40.8% | 12.0 years |
| Japan, en.wikipedia (symmetric) | 304 | 125 | 179 | 41.1% | 17.0 years |

### Table 2. Cohort sizes by formation period, n (deaths)

| Cohort | Japan | Korea |
|---|---|---|
| 1996–2000 | 37 (27) | 28 (15) |
| 2001–2005 | 51 (33) | 28 (15) |
| 2006–2010 | 122 (73) | 57 (29) |
| 2011–2015 | 349 (206) | 141 (78) |
| 2016–2020 | 416 (217) | 162 (68) |
| 2021–2025 | 371 (76) | 133 (19) |

### Table 3. Cumulative attrition, 1 − S(t), with 95% confidence intervals

| Elapsed years | Japan (primary) | Korea (primary) | Japan (symmetric) |
|---|---|---|---|
| 1 | 6.8% (5.5–8.2) | 6.4% (4.6–8.8) | 3.9% (2.3–6.8) |
| 2 | 13.1% (11.3–15.0) | 13.1% (10.5–16.2) | 7.9% (5.4–11.6) |
| 3 | 19.7% (17.7–22.0) | 20.1% (16.9–23.8) | 12.0% (8.8–16.3) |
| 5 | 33.0% (30.4–35.7) | 31.8% (27.9–36.2) | 22.3% (17.9–27.5) |
| 7 | 43.5% (40.6–46.6) | 41.6% (37.2–46.3) | 28.1% (23.2–33.8) |
| 10 | 53.9% (50.7–57.1) | 48.4% (43.6–53.3) | 37.2% (31.6–43.4) |
| 15 | 62.9% (59.3–66.4) | 51.5% (46.4–56.8) | 47.9% (41.5–54.7) |

### Table 4. Log-rank tests

| Comparison | Panel | χ² | df | p |
|---|---|---|---|---|
| Japan vs Korea (primary; source-asymmetric) | n = 1,895 | 5.80 | 1 | 0.016 |
| Japan vs Korea (symmetric layer) | n = 853 | 4.23 | 1 | 0.040 |
| Sex (Japan, primary) | n = 1,258 | 6.96 | 1 | 0.008 |
| Sex (Korea, primary) | n = 510 | 15.16 | 1 | < 0.001 |
| Cohort (Japan, primary) | n = 1,346 | 10.35 | 5 | 0.066 |
| Cohort (Korea, primary) | n = 549 | 4.37 | 5 | 0.498 |

Comparisons across countries use panels built from different encyclopedias and are reported for completeness rather than as evidence of national difference.

### Table 5. Discrete-time conditional hazards, h(t) = deaths / risk set

| Elapsed years | Japan (primary) | Korea (primary) | Japan (symmetric) |
|---|---|---|---|
| 1 | 6.0% (80/1,335) | 5.7% (31/545) | 3.6% (11/303) |
| 2 | 6.8% (81/1,200) | 7.2% (35/489) | 4.2% (12/289) |
| 3 | 7.7% (82/1,067) | 8.1% (35/432) | 4.4% (12/271) |
| 4 | 8.2% (75/915) | 7.7% (28/366) | 5.3% (13/247) |
| 5 | 9.0% (71/788) | 7.6% (24/317) | 6.7% (15/223) |
| 6 | 8.6% (56/651) | 5.4% (15/278) | 3.9% (8/203) |
| **7** | 7.9% (43/546) | **9.5% (23/243)** | 3.7% (7/187) |
| 8 | 7.7% (35/456) | 4.4% (9/204) | 2.4% (4/166) |
| 9 | 6.7% (26/388) | 5.0% (9/180) | 6.4% (10/157) |
| 10 | 5.2% (17/329) | 2.6% (4/151) | 4.3% (6/138) |
| 11 | 5.5% (15/275) | 1.6% (2/124) | 3.9% (5/127) |
| 12 | 6.8% (15/219) | 1.8% (2/110) | 8.1% (9/111) |

### Table 6. Excess-hazard test at t = 7 against pooled neighbours (t = 5, 6, 8, 9)

| Panel | h(7) | Neighbour baseline | Ratio | p (one-sided) |
|---|---|---|---|---|
| Korea (primary) | 9.5% (23/243) | 5.8% | **1.63** | **0.016** |
| Japan (primary) | 7.9% (43/546) | 8.2% | 0.96 | 0.642 |
| Japan (symmetric) | 3.7% (7/187) | 4.9% | 0.76 | 0.821 |

### Table 7. Falsification checks on the seven-year concentration

| # | Alternative explanation | Result |
|---|---|---|
| 1 | t = 7 is the lucky year among many tested | Testing t = 2…12: Korea significant at t = 7 only, and largest ratio of 11; Japan significant nowhere, t = 7 ranks 9th of 11 |
| 2 | A calendar-year dissolution wave | Deaths at t = 7 spread over 2014–2026; deleting the modal year leaves ratio 1.53, p = 0.041 |
| 3 | A single parser's artifact | Share of deaths at t = 7 by source: category 11.0%, infobox 7.5%, lead text 11.8% |
| 4 | Sensitivity to neighbourhood choice | Four alternative baselines give ratios 1.48–1.90, all p < 0.05 |
| 5 | Japanese null depends on death definition | Ratios 1.02 / 0.96 / 0.93 (conservative / strict / loose), none significant |
| 6 | Cohort dependence | 2009–2025 formations: ratio 2.09, p < 0.001 (n = 465). 1996–2008: ratio 0.28 (n = 84; 54 at risk at t = 7, underpowered) |
| 7 | Editorial rounding toward the contract narrative | **Cannot be excluded** — see Limitations 3 |

### Table 8. Complementary log-log discrete-time hazard models

| Specification | Term | Hazard ratio | 95% CI | p |
|---|---|---|---|---|
| Pooled symmetric layer (853 groups, 7,199 person-periods) | t = 7 (Japan, reference country) | 0.65 | 0.30–1.44 | 0.291 |
| Pooled symmetric layer | t = 7 × Korea | **2.72** | 1.07–6.88 | **0.035** |
| Korea (primary), fitted alone | t = 7 | 1.78 | 1.09–2.90 | 0.021 |
| Japan (primary), fitted alone | t = 7 | 0.93 | 0.67–1.29 | 0.650 |

Baseline hazard modelled as a cubic polynomial in t, estimated separately by country.

### Table 9. Cox model A — pooled, source-symmetric layer (n = 853; 349 events; concordance 0.597)

| Covariate | Hazard ratio | 95% CI | p | Schoenfeld p |
|---|---|---|---|---|
| Country: Korea | 1.55 | 1.23–1.96 | < 0.001 | 0.417 |
| Sex: male | 0.50 | 0.40–0.64 | < 0.001 | 0.141 |
| Sex: mixed | 0.58 | 0.28–1.19 | 0.137 | 0.180 |
| Sex: unknown† | 0.39 | 0.21–0.74 | 0.004 | 0.119 |
| Cohort 2001–2005 | 0.83 | 0.48–1.42 | 0.487 | 0.850 |
| Cohort 2006–2010 | 0.76 | 0.48–1.22 | 0.261 | 0.442 |
| Cohort 2011–2015 | 0.78 | 0.50–1.21 | 0.271 | 0.715 |
| Cohort 2016–2020 | 0.83 | 0.53–1.30 | 0.416 | 0.761 |
| Cohort 2021–2025 | 0.66 | 0.37–1.16 | 0.148 | 0.956 |

References: Japan, female, cohort 1996–2000. † Missingness indicator; not interpreted (see Methods).

### Table 10. Cox model B — Japan only, with agency size (n = 1,346; 632 events; concordance 0.570)

| Covariate | Hazard ratio | 95% CI | p | Schoenfeld p |
|---|---|---|---|---|
| Sex: male | 0.62 | 0.47–0.83 | 0.001 | 0.293 |
| Sex: mixed | 1.97 | 1.10–3.52 | 0.023 | 0.538 |
| Sex: unknown† | 0.57 | 0.38–0.84 | 0.005 | 0.851 |
| Agency size 2–4 groups | 0.79 | 0.63–0.98 | 0.033 | 0.233 |
| Agency size 5–9 groups | 1.10 | 0.82–1.47 | 0.522 | 0.813 |
| Agency size 10+ groups | 1.23 | 0.96–1.57 | 0.099 | 0.524 |
| Agency size unknown† | 0.88 | 0.70–1.11 | 0.275 | **< 0.001** |
| Cohort 2001–2005 | 0.89 | 0.53–1.51 | 0.674 | 0.313 |
| Cohort 2006–2010 | 0.77 | 0.48–1.22 | 0.260 | 0.125 |
| Cohort 2011–2015 | 0.88 | 0.57–1.35 | 0.556 | **0.001** |
| Cohort 2016–2020 | 1.16 | 0.75–1.78 | 0.510 | **0.035** |
| Cohort 2021–2025 | 0.96 | 0.60–1.54 | 0.853 | 0.067 |

References: female, single-group agency, cohort 1996–2000. † Missingness indicator; not interpreted. Bold Schoenfeld p values mark covariates for which proportionality is rejected.

### Table 11. Sensitivity analyses

| Variation | Japan n | Japan 3-year | Korea n | Korea 3-year | Korea t = 7 ratio (p) |
|---|---|---|---|---|---|
| Primary (1996–2025, strict) | 1,346 | 19.7% | 549 | 20.1% | 1.63 (0.016) |
| Window 2009–2025 | 1,207 | 19.4% | 465 | 21.1% | — |
| Window 1996–2022 | 1,151 | 20.6% | 465 | 21.3% | — |
| Death definition: conservative | 1,346 | 14.6% | — | — | 1.02 (0.473) ‡ |
| Death definition: loose | 1,346 | 20.6% | — | — | 0.93 (0.711) ‡ |
| Definition-sensitive groups removed | 1,234 | 20.2% | — | — | — |
| Korea: year-unknown deaths excluded | — | — | 503 | 22.0% | 1.64 (0.014) |

‡ Japanese ratio under that definition. The Korean panel supports only one death definition.

### Table 12. RIAJ certification attainment, Japanese panel (n = 1,346)

| Tier | Groups reaching | Share of panel |
|---|---|---|
| Gold | 94 | 6.98% |
| Platinum | 44 | 3.27% |
| Double Platinum | 26 | 1.93% |
| Triple Platinum | 17 | 1.26% |
| Million | 14 | 1.04% |
| Double Million | 4 | 0.30% |
| Triple Million | 1 | 0.07% |

Any certification: 105 groups (7.8%).

### Table 13. Contract institutions compared

| | Korea | Japan |
|---|---|---|
| Government-issued standard exclusive contract | Yes (KFTC 2009; MCST current) | No |
| Numeric benchmark on contract term | **Seven years** | None |
| Form of regulation | Ex ante uniform standard | Ex post case-by-case (competition law) |
| Text at promulgation (singer-centred, 2009) | Right to terminate after seven years elapsed, effective six months after notice | — |
| Current text (2024-0021) | Term may not exceed seven years; extension by written agreement | Exclusivity within a "reasonably necessary scope"; no numeric limit |

## Figure Legends

**Figure 1. Kaplan–Meier survival curves.** Survival probability against years since formation for the Japanese primary panel (n = 1,346), the Korean primary panel (n = 549), and the source-symmetric Japanese panel (n = 304). Shaded bands are 95% confidence intervals. The two primary curves track one another closely through the first decade.

**Figure 2. Discrete-time conditional hazards by year since formation.** Hazard h(t) = deaths in year t divided by the risk set entering year t, for the same three panels, t = 1…12. The Korean series dips at t = 6, peaks at t = 7, and falls at t = 8; the Japanese series peaks at t = 5 and declines smoothly. Later years rest on thin risk sets and should be read with that in mind.

**Figure 3. Survival by sex.** Kaplan–Meier curves for male and female groups in the Japanese and Korean primary panels. Male groups show longer survival in both countries.

All figure labels are in English.
