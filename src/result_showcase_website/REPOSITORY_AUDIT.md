# Repository and notebook audit

Review date: 2026-11-16. Cell references below are zero-based. This is a review of the local snapshot, not a certification of external F1 records. Original notebooks and existing user edits were preserved. All new deliverables are confined to `src/result_showcase_website/`.

## Scope and evidence levels

All project Python source files, five notebooks (markdown, code and saved text outputs), configuration, README and dependency declarations were examined. Data directories were inventoried; existing CSVs were read for targeted independent verification. Cached JSON documents are grouped by function; each is listed in `evidence/repository-inventory.csv`. Dependencies in `.venv` and `.git` internals are not project-authored analytical files and are excluded.

“Reproduced” below means targeted read-only checks independently reconstructed selected quantities from the existing CSVs. It does not mean the original notebooks or pipelines were executed. “Supported” means code and saved evidence agree subject to stated assumptions. Figures were copied byte-for-byte from existing outputs, never regenerated from invented points.

Three Python verification tests pass: career-statistic reconstruction; lap-filter and headline-result reconstruction; original figure-byte provenance. JavaScript checks are documented in README. The full SciPy permutation simulation was not rerun; the host lacks SciPy. The browser tool rejects file URLs; visual browser QA is incomplete. No production/data pipeline was run and no external data was fetched to replace the repository snapshot.

## Project files: responsibilities and issues

| File | Responsibility | Review |
|---|---|---|
| `README.md` | Project introduction and old file list. | Stale: “75 years” contradicts 1996–2026; many paths predate fetch/build subfolders; lists package files absent in this working tree. |
| `requirements.txt` | pandas, matplotlib, BeautifulSoup, requests, FastF1. | Career notebook additionally imports seaborn, scipy, numpy and IPython; notebook environment needs ipykernel/Jupyter. Direct requirements should be explicit and version-compatible. |
| `.gitignore` | Ignore environments, caches, partial downloads, one processed CSV. | Last entry `.gitignoredata/raw/fastf1_cache/` appears accidentally concatenated and does not ignore the intended cache. Ignores `lap_times.csv`, not the consumed `lap_times_cleaned.csv`. |
| `.vscode/settings.json` | WSL terminal default and LF line endings. | Editor configuration, no analysis. |
| `src/f1_analysis/api.py` | Shared atomic JSON writes, retries, HTTP-429 handling, pagination, resumable partial downloads. | Existing final files return immediately without freshness revalidation; ongoing seasons can become stale. Do not assume cached means current. |
| `scripts/fetch/fetch_races.py` | Download calendars and completed-race lap pages since 1996. | Root uses `parents[1]` from nested fetch directory: resolves to `scripts`, breaks package import/data root. Writes nested `laps/YEAR/round_NN.json`, while lap builder expects flat `YEAR_round_NN.json`. Missing shebang. |
| `scripts/fetch/fetch_results.py` | Fetch yearly race-result pages 1996–2026. | Same wrong root. Writes `data/raw/YEAR.json`, while builder expects `data/raw/results/YEAR.json`. Missing shebang. |
| `scripts/fetch/fetch_pitstops.py` | Concurrent, rate-limited pit-stop caching with legacy-page reuse. | Correct root. Actual years 2011–2026, stale docstring says through 2024. Calendars include rounds without date filtering; empty future caches may remain stale because existing files are skipped. |
| `scripts/fetch/fetch_fastf1_circuits.py` | Fetch qualifying circuit metadata and corner positions, resume per event, stop on rate limits. | Correct root; useful metadata inventory. No historical lap-path geometry or causal pace model is produced. Completeness uses row counts, not unique-corner validation. |
| `scripts/fetch/fetch_circuits_wiki.py` | Cache HTML and scrape circuit table to raw CSV. | Relative paths require root working directory. Emits `Last length used`, whereas cleaner expects pre-split numeric km/mile columns; pipeline needs a parsing step. |
| `scripts/clean_dataset_cricuit.py` | Normalize circuit strings, numeric columns, footnotes, validate units. | Typo retained in filename. Reads `wikipedia_circuits.csv`, while fetch writes `wikipedia_circuits_raw.csv`. Also expects split length columns not emitted by scraper. |
| `scripts/clean_fastf1_circuits.py` | Clean numeric metadata, sort and deduplicate events/corners. | Drops `CornerLetter` before deduplicating by corner number, potentially collapsing distinct lettered corners. Requires validation against source corner identity. |
| `scripts/check_circuit_data.py` | Load qualifying sessions 2018–2024 and report circuit metadata availability. | `parents[2]` points above repo for a top-level scripts file. Creates directories/configures FastF1 on import; not a pure read-only check. |
| `scripts/build/build_dataset_lap_times.py` | Flatten paginated lap JSON; validate offsets/counts; atomic CSV. | Wrong `parents[1]` root. Accepts flat filenames only; incompatible with current fetch layout. |
| `scripts/build/build_dataset_races.py` | Choose latest dated calendar snapshot and flatten to CSV. | Wrong root; scans date subfolders only, while stored calendars are flat. Writes processed/races, but career notebook reads raw/races.csv. Missing shebang. |
| `scripts/build/build_dataset_results.py` | Flatten results, check duplicates and total record count, atomic replacement. | Wrong root; writes processed/results, while notebooks read raw/results.csv. Missing shebang. |
| `scripts/build/build_dataset_pitstops.py` | Flatten dict/list responses, deduplicate identical stops and reject conflicts. | Correct root, but does not validate reported pagination total. Writes `pit_time`/`pit_duration`. Missing shebang. |
| `scripts/build/build_pitstops.py` | Alternative pit-stop builder with pagination offset/total validation. | Writes same destination with different schema (`pit_stop_time`/`duration`, extra race metadata). Choose one canonical builder before future pipeline use. |

At review start Git already showed a modified notebook 03 and deleted `src/f1_analysis/{__init__,processing,scraping,statistics,visualization}.py`. These were not restored or edited. Their old README descriptions do not describe the current filesystem. An absent `__init__.py` alone does not preclude a namespace package; incorrect import roots are the concrete issue.

## Data families and what each file represents

| Path | Role |
|---|---|
| `data/raw/laps/*.json` (588 files) | Cached paginated lap timings for the season/round encoded in each filename. |
| `data/raw/results/*.json` (31 files) | Cached result pages for one season. |
| `data/raw/races/*.json` (31 files) | Cached calendar pages for one season; calendar presence is not lap coverage. |
| `data/raw/pitstops/*.json` (330 files) | Cached pit-stop responses for one season/round; empty responses must not be treated as complete future data. |
| `data/raw/lap_times.csv` | Flattened driver-lap durations and race metadata; notebook 01 input. |
| `data/raw/results.csv` | Driver-race entries, points, classifications, constructor, birth date, fastest-lap fields; career and team joins. |
| `data/raw/races.csv` | Race calendar/locations; inspected by career EDA. |
| `data/raw/pitstops.csv` | Stop identifiers, lap numbers, timing fields; exact-lap filter in pace notebooks. |
| `data/raw/wikipedia_circuits_raw.csv` | Raw scraped circuit types, names, turns and combined length string. |
| `data/raw/fastf1_circuits_raw.csv` | Event/circuit metadata and corner counts. |
| `data/raw/fastf1_corners_raw.csv` | Corner number/letter and X/Y/angle/distance per event. Not a full racing-line trace. |
| `data/processed/wikipedia_circuits_cleaned.csv` | Cleaned, split numeric length and turns; pace circuit features. |
| `data/processed/fastf1_circuits.csv` | Normalized event-level FastF1 metadata. |
| `data/processed/fastf1_corners.csv` | Normalized corner-level metadata after letter removal/deduplication. |
| `data/processed/laps/lap_times_cleaned.csv` | All 639,293 lap rows plus numeric seconds; consumed by notebooks 02/03. |

## Notebook-by-notebook claim review

### 00_build_dataset_csvs

Cell 2 calls `../scripts/build_dataset_lap_times.py`; the file now resides in `scripts/build/`. The saved 639,293/588 output agrees with the snapshot but the current command cannot reproduce it without path fixes. “CSVs are not synced” is stale relative to this working tree’s present files. The notebook builds only the lap CSV, not the full pipeline.

### 01_lap_times_eda

| Cells / finding | Verdict |
|---|---|
| 0–9: row/key meaning, counts, missingness, duplicate and metadata checks | Sound descriptive checks. Independent test confirms 639,293 distinct driver-race-lap rows, 588 races, 42 circuits, 149 drivers. Saved missingness and metadata checks are internally coherent. |
| 10–11: duration parsing, hours/minutes/seconds | Sound for observed formats; independent parser matches every processed duration to raw duration text. Parser intentionally rejects seconds ≥60 without colon representation, so not a universal duration parser. |
| 12–14: coverage and driver/circuit exposure | Correctly presented as observed coverage, not calendar completeness or driver quality. |
| 15–19: outliers, log distributions, central-98% view, circuit boxplots | Correct distinction between presentation zoom and data removal. Unusually long laps alone cannot identify the event cause. |
| 20–22: sequence gaps and positions | Correctly limited to internal gaps and observed starts; cannot infer trailing laps or failure causes. |
| 23–26: selected race, shared slow periods, opening-lap context | Exploratory only; selected drivers are those with most laps, not necessarily teammates. Equal lap number need not be equal clock time. |
| 27–29: findings and limitations | Mostly appropriately qualified. No driver/car causal conclusion. |
| 30–31: processed export | **Pipeline mismatch:** writes `lap_times.csv`; later notebooks require `lap_times_cleaned.csv`. Existing saved output does not resolve this mismatch. |

### 02_lap_performance

| Cells / finding | Verdict |
|---|---|
| 0–10: question, joins, missingness, pit markers and relative features | Many-to-one validation protects lap counts. Pit availability is correctly unknown pre-2011. Required feature checks support internal validity but not historical truth. |
| 11–12: extreme durations | Correct diagnostic counts/inspection; not proof of erroneous timing. |
| 13: “verified red flag” (Canada 2011, lap 25) | **Unsupported provenance within repository:** code hard-codes the label without a cited race-control source. Treat as event interpretation, not a verified data field. Website uses “candidate shared delay.” |
| 14–16: interruption heuristic and pace sample | Reproduced: 56 candidate race-laps, 577,990 retained laps, 587 races. It is not an exhaustive detector of red flags/safety cars. |
| 17–19: circuit plots, correlations and circuit-type difference | r=.756, r=.087 and type medians reproduced. 1.14% is relative difference of medians, not a causal effect or tested significant difference. |
| 20–24: pairing, extreme gap counts and 2024 driver chart | Pair count, median, >5 s count, Verstappen/Norris examples reproduced. Replacement drivers can make season medians non-symmetric (Ferrari/RB/etc.). Both signed records must not count as independent pairs. |
| 25–26: histogram/conclusion | Same substantive teammate conclusion as 03. Histogram applies ≤5 s filter, whereas .611 s describes pairs before that extra filter. No skill ranking established. |
| 27–32: constructor relative pace and consistency | McLaren summary reproduced; saved full ranking is consistent with 03. Eligibility/aggregation is sensible for descriptive analysis. Box width is not an inferential variance test. |
| 33–36: race progression | Endpoints reproduced. −.742481% rounds to −.74%, not −.75% at two decimals; website uses −.742%. Final phase is slightly slower than 80–90%, so trend is not strictly monotonic. Fuel mechanism untested. |

### 03_lap_time_analysis

This notebook is a streamlined presentation of the lap-performance analysis, not an independent replication dataset.

| Cells / finding | Verdict |
|---|---|
| 0–6: scope, data assembly and filters | Clear scope: four analyses, no dedicated pit-impact analysis. Preserves data and labels heuristics appropriately. Same export-name dependency issue as 02. |
| 7–12: circuit results | Numerical findings reproduced. Sentence “corner geometry and speed matter more” is stronger than its evidence: those variables were not modeled. Website treats this as an untested explanation. No p-values were computed for Pearson correlations or street-vs-race medians. |
| 13–18: teammate results | Main figures reproduced; the .611 s result is unfiltered only with respect to the additional 5 s gap rule, not raw unfiltered laps. No attribution solely to skill. |
| 19–24: constructor results | Main metric reproduced; saved ordering supported. Describes total package. Cell 23 overwrites the ≥8-race summary without that rule; all ten currently pass, so snapshot unchanged, but future generalization should preserve filter. |
| 25–28: progression | Reproduced endpoints and supported descriptive trend. Last phase value should be −.742% / −.74%, not −.75% at two decimal precision. ≥90% survivor selection and changing per-phase sample composition matter. |
| 29: overall findings | Suitable qualified summary. No factor contribution percentages, no causal estimate, no validated predictive result. |

### 02_driver_career_eda

| Cells / finding | Verdict |
|---|---|
| 0–10: selection and coverage | 15 of 20 deliberately selected names present; correct limitation to 1996 onward. `Path.cwd().parent` assumes notebook working directory, unlike robust root search in lap notebooks. |
| 11–14: race ages, seasonal results, reconstructed rank | Definitions match code. Ranking uses all drivers, which avoids ranking only the selected cohort. Still omits Sprint points/official tie-breaks and should not be labeled official championship ranking without qualification. |
| 15–21: debut mapping and career-year calculation | Elapsed calendar year is correctly distinguished from active seasons; pre-1996 careers are left-censored. Debut mapping is hard-coded, not derived from source coverage. |
| 22–29: complete seasons and peak construction | Excludes 2026; chooses all seasons tied at minimum rank; 15 drivers, 36 records and 10/3/2 rank groups reproduced. Driver ages are rounded before statistical testing; avoid that in future analysis. |
| 30–40: peak plots and heatmap | Descriptive age/career variation is supported. Heatmap is repeated best results, not duration of continuous optimum. Age/experience cannot be treated as independent predictors. |
| 41–46: Welch comparison | Reproduced from CSVs: means 28.347/27.278, t≈.726, df≈10.806, p≈.4832. CI [−2.179,4.317] is consistent with standard Welch CI formula. Correct non-rejection. Small selected cohorts restrict inferential interpretation. |
| 47–55: early/later construction | Correct first-three-participation-seasons split; excludes left-censored careers and 2026; 12 eligible drivers. Later follow-up varies substantially. |
| 56, 59, 61: “no saved output” statements | **Stale:** corresponding tables/plots exist in current saved notebook. Website includes the actual saved figures. |
| 57–62: scatter and win/podium rates | Correct directional reading for ranks and rates per recorded entry. Entry count is not necessarily official starts; do not silently change denominator wording to starts. |
| 63–65: Spearman hypotheses/results | Rho .5804 and .1418 independently reproduced. Approximate p=.0479 must not be cherry-picked while omitting permutation/multiplicity results. |
| 66–68: permutation and Holm | Code uses valid pairing randomization for an exchangeable independence null; merely zero monotonic correlation is a weaker null. Reported p=.0527/.6596 and adjusted .1054/.6596 are arithmetically consistent. RNG 42, 99,999 randomized permutations; simulation not rerun here. |
| 69 §10.1: first rank-1 career years 2–10 | **Incorrect:** Rosberg’s table has career year 11. Correct observed range is 2–11. Other mean-age/recorded-season statements agree with saved evidence. |
| 69–72: answer, limitations, conclusion | Generally well qualified: no universal peak, no significant age difference, no established predictive ability. “No relationship” would overstate non-significance. Stronger population statements are inappropriate for this selected sample. |
| 73 | Empty markdown, no analytical content. |

## Statistical interpretation

Welch H₀: equality of two mean driver-level peak-age measures; two-sided H₁. Effect +1.069 years, wide CI including zero. Welch does not require equal variances, but independence and well-behaved mean distributions remain assumptions. A non-significant result does not prove equality.

The Spearman comparison is driver-level, not lap-level. Positive rho means higher numerical early ranks tend to accompany higher numerical later ranks (both worse). The permutation independence null requires exchangeability across the selected drivers; shared eras/teams and selection may weaken it. Holm controls the two specified comparison family under appropriate valid p-values; it does not remove selection bias or account for every exploratory question in the project.

Use “p-value,” not “p-score.” P-values are not the posterior probability of H₀ or effect sizes. There is no z-score/z-test reported, and a normal z approximation should not replace the Welch t reference distribution. The pooled Student test assumes equal variances; it was not the test executed in the notebook.

Primary method references: [SciPy ttest_ind](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html), [Spearman guidance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html), [permutation_test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).

## Priority follow-up work (not executed)

1. Unify project-root calculations, paths, flat/nested cache conventions and output CSV locations. Fix notebook 00 command and notebook 01 export name.
2. Choose one pit-stop builder/schema and add Wikipedia length parsing between scrape and clean.
3. Make notebook dependencies explicit, remove in-notebook install side effects, preserve full precision until display.
4. Add historical layouts, tyre/stint/flag data and race-matched comparisons before causal or stronger inferential claims.
5. Use larger career cohorts and out-of-sample validation for prediction; account for era, machinery, censoring and unequal follow-up.

These issues do not automatically invalidate the stored snapshot’s arithmetic. They do prevent an unqualified claim that the current end-to-end pipeline is reproducible as written.
