# Project memory: F1 driver versus car

Reviewed 2026-11-16. Preserve these distinctions when continuing the project. Sources are the five notebooks, their saved outputs, and repository CSVs. This document and the website are a fixed snapshot, not live results.

## Central question

Which factors are associated with F1 lap pace, when do selected drivers achieve their best recorded seasonal results, and do early results associate with later success?

**No analysis here identifies the isolated contribution of the driver or car.** Do not produce a “driver X%, car Y%” split. There is no causal model, variance-components model or validated prediction model.

## Data and definitions

- Lap snapshot: 639,293 timings, 588 observed races, 42 circuit IDs, 149 drivers, 31 season labels from 1996 through partial 2026. Saved dates span 1996-03-10 to 2026-11-08. This is not 75 years of data.
- Lap position is position at that lap, not finishing position. A row is a driver–race–lap; repeated lap records are not independent experiments.
- EDA retains every source row. 16 positions and 150,951 start times are missing. No duplicate lap keys are reported. Ten internal gap transitions and three late-start driver-race groups do not explain the missingness or identify all missing trailing laps.
- The processed file currently present is `data/processed/laps/lap_times_cleaned.csv`; notebook 01 instead writes `lap_times.csv`. Reconcile before rerunning the chain.
- Pace selection excludes lap 1, matched pit laps, candidate shared extreme delays and values outside ±20% of the race median. Remaining: 577,990 laps across 587 races. Candidate shared delays: 56 race-laps. These are not complete safety-car/red-flag labels.
- Pit-stop records begin in 2011. Missing earlier records are unknown, not zero. Out-laps and unrecorded stops can remain.
- Wikipedia length/turn metadata is one snapshot mapped to all historical seasons. FastF1 corner data is collected but not used to establish the published pace conclusions.

## Questions answered by 02_lap_performance and 03_lap_time_analysis

| Question | Observed answer | Interpretation limit |
|---|---|---|
| Does circuit length relate to absolute lap time? | Pearson r = 0.756 across 42 circuit summaries. | Descriptive; distance naturally affects time, historical layouts differ. |
| Does turn count relate to distance-normalized pace? | Pearson r = 0.087. | Weak linear association; does not exclude nonlinear effects or prove corner geometry is more important. |
| Are street circuits slower per km? | Median 18.149 s/km (10 circuits), versus 17.945 (32 race circuits), about 1.14% higher. | No reported significance test; unequal eras and circuit mix. |
| Do teammates differ? | Median absolute gap 0.611 s among 242,133 unique paired laps. | After pace selection, before the additional gap cutoff. Does not isolate skill. |
| Which selected 2024 teammate gaps stand out? | Verstappen −0.564 s, Norris −0.2115 s; Russell −0.013 s, Hamilton +0.013 s. | Within-team signed differences; ≤5 s absolute gap and ≥100 paired laps. No all-driver skill ranking. |
| How much does the gap cutoff remove? | 8,913 unique pairs, 3.68%, exceed 5 s. | Cutoff can remove genuine differences as well as disruption. |
| Which constructor has the fastest 2024 relative median? | McLaren −0.929581%; Ferrari −0.758811%; Red Bull −0.682148%; Mercedes −0.521756%. | Driver–car–team result; race eligibility differs. No significance claim. |
| Is constructor performance equally consistent? | Saved boxplot suggests Red Bull has a narrower central range than Mercedes. | Descriptive visual comparison; unequal circuit/race coverage, no variance test. |
| Do laps become faster through a race? | First phase +1.431974%; final phase −0.742481%; minimum −0.826681% at 80–90%. | Relative to each driver-race median; survivors reaching ≥90% distance, phase composition differs. Not strictly monotonic. |
| Do pit stops or lower fuel cause the differences? | Not answered. | Pit stops are filtering inputs; fuel, tyres and strategy are not independently modeled. |

Constructor method: compare a lap to the median of ≥6 drivers at the same race-lap; aggregate median per driver-race with ≥10 laps; average exactly two eligible teammates; require ≥5 eligible constructors per race; take each constructor’s median over ≥8 eligible 2024 races. Same lap number need not equal the same time on track.

| Constructor | Relative median (%) | Eligible races |
|---|---:|---:|
| McLaren | -0.929581 | 24 |
| Ferrari | -0.758811 | 24 |
| Red Bull | -0.682148 | 21 |
| Mercedes | -0.521756 | 23 |
| Aston Martin | 0.202931 | 20 |
| Haas | 0.273125 | 23 |
| Alpine | 0.372063 | 20 |
| Williams | 0.405951 | 19 |
| RB | 0.420290 | 21 |
| Sauber | 0.778982 | 22 |

## Questions answered by 02_driver_career_eda

Twenty drivers were initially selected; fifteen appear in the 1996–2026 results. This is a deliberately selected cohort, not all drivers and not a random sample. Exclude partial 2026 for peak and early/later analyses.

**Rank:** season sum of available race points, ranked across all source drivers with `method='min'`. Missing Sprint points, exclusions and official tie-breaks can make this differ from official championship standing. Prefer “recorded points rank” to unqualified “championship rank.” Raw points across eras are not comparable performance units.

**Peak:** all complete observed seasons tied at each driver’s best recorded rank. First compute average race age for each season, then average ages across the driver’s peak seasons. There are 36 such driver-season records. Ten drivers have best rank 1, three rank 2, two rank 3.

| Driver | Mean peak age | Best rank |
|---|---:|---:|
| Alonso | 24.42 | 1 |
| Vettel | 24.56 | 1 |
| Verstappen | 25.33 | 1 |
| Norris | 25.70 | 1 |
| Räikkönen | 27.73 | 1 |
| Button | 29.48 | 1 |
| Häkkinen | 30.27 | 1 |
| Rosberg | 31.08 | 1 |
| Hamilton | 31.42 | 1 |
| Schumacher | 33.48 | 1 |
| Leclerc | 24.76 | 2 |
| Massa | 27.22 | 2 |
| Barrichello | 31.09 | 2 |
| Ricciardo | 26.06 | 3 |
| Montoya | 27.26 | 3 |

- **When do drivers peak?** No universal age follows from the sample. Rank-1 drivers’ mean of driver-level peak ages is 28.347 years. First recorded rank-1 seasonal average ages range from about 23.0 (Vettel) to 31.5 (Schumacher). Schumacher’s earlier career is not observed.
- **After how much experience?** First rank-1 seasons range from calendar career year 2 (Hamilton) to 11 (Rosberg). The notebook’s 2–10 claim is incorrect. Career year includes absences, so it is not active-season count. Age and career year are mathematically related.
- **Is success sustained?** Hamilton has seven recorded rank-1 seasons; Schumacher five; Vettel and Verstappen four; Alonso and Häkkinen two. These are counts, not necessarily consecutive intervals or complete career totals.
- **Do rank-1 drivers peak later?** Mean 28.347 (n=10, SD 3.240) versus 27.278 (n=5, SD 2.364). Difference +1.069 years; Welch t=0.726, df≈10.806, two-sided p=0.4832, 95% CI [−2.179, 4.317]. Do not reject equal means at α=.05. This does not establish equivalence.
- **Do early results indicate later results?** Twelve eligible drivers; remove Schumacher, Häkkinen and Barrichello because their debuts predate coverage. Early means first three actual participation seasons, not first three calendar years (Alonso: 2001/2003/2004; Massa: 2002/2004/2005). Later uses subsequent observed complete seasons.

| Comparison | Spearman rho | Approximate p | Permutation p | Holm-adjusted p |
|---|---:|---:|---:|---:|
| Early mean rank / later mean rank | 0.5804 | 0.0479 | 0.0527 | 0.1054 |
| Early mean rank / later best rank | 0.1418 | 0.6602 | 0.6596 | 0.6596 |

No rejection after Holm adjustment at .05. Positive rho on a rank scale means better early performance tends to accompany better later performance. The first coefficient is moderate in this sample; the second weak. Neither demonstrates reliable prediction or causation. Different follow-up lengths and team strength confound comparisons.

Permutation procedure: 99,999 randomized pairings, RNG seed 42, two-sided SciPy test. Under the permutation null, pairings must be exchangeable (an independence null); merely zero Spearman correlation is not sufficient in all distributions. The two tests are one Holm family. Permutation p-values have Monte Carlo uncertainty and are not exact enumeration results.

## Statistical language to retain

- Say **p-value**, not p-score. It is a tail probability under the null and assumptions, not P(H₀ true).
- Welch’s unequal-variance t-test is appropriate to the stated comparison; it still assumes independent observations and well-behaved means. Small, selected groups limit inference.
- Pooled Student’s t-test adds an equal-variance assumption. No pooled Student test or z-test is reported here. A standardized z-score is not interchangeable with Welch’s t-statistic.
- Non-significance does not prove no effect; the confidence interval is wide. The tests are exploratory.
- The notebook rounds driver-level peak ages to two decimals before testing. The saved t/p reproduce that rounded input. For a future analysis, retain full precision until display.

## Unanswered research and next steps

Resolve paths/schema mismatches before reruns; use historical circuit layouts; align comparisons by race and stint/tyre conditions; account for clustering by race/driver/season; assess filter sensitivity; use matched race-level tests or hierarchical models for pace comparisons; expand the career cohort and validate forecasts out of sample. None of these analyses has been performed in this showcase.
