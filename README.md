# F1 Driver vs Car — The Science of Speed

**What makes the difference in Formula 1: the driver, the car, or the conditions?**

This project explores race pace and driver career progression using Formula 1 lap timings, race results and circuit characteristics. Python notebooks contain the analysis; an F1-inspired website presents the questions, graphs, findings and statistical uncertainty.

**Created by Nigel Xherimeja, Sejbi Koromani and Sara Petro.**

The analysis describes associations. It does not isolate driver skill from machinery or assign a percentage of performance to the driver versus the car.

## Quickstart: view the results

Download or clone this repository and open a terminal in its root folder (`f1-driver-vs-car`). To launch the website, run:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory src/result_showcase_website
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Stop the server with **Ctrl+C**.

On Windows, use `python` instead of `python3` if necessary. The server only requires Python 3: **no dependency installation, npm build, API key or data download is needed to view the results**. Alternatively, open `src/result_showcase_website/index.html` directly in a modern browser.

The website uses the **Science of Speed** redesign: an animated racing-line hero, timing-screen charts, career timelines and a light statistics section. The repository’s original results, evidence and figures remain available.

The website includes:

- Interactive views of 2024 constructor pace and teammate gaps.
- Circuit comparisons, race-progression charts and driver career findings.
- Explanations of null hypotheses, Welch’s t-test, Spearman correlation, permutation tests and p-values.
- Four readable notebook pages with saved tables/charts, collapsible code and original `.ipynb` downloads.
- Original notebook figures and links to the evidence and repository audit.

For implementation details, see the [website README](src/result_showcase_website/README.md).

## What questions are we answering?

| Research question | How we investigate it |
|---|---|
| How do circuit length, turns and circuit type relate to lap times? | Compare circuit-level median times and distance-normalized pace. |
| Do teammates achieve different lap times? | Match drivers from the same constructor, race and lap number. |
| How does observed pace differ between constructors? | Compare lap times with the grid median, then aggregate by driver-race and constructor-race. |
| Do lap times change as a race progresses? | Compare race phases relative to each driver’s race median. |
| At what age and career stage do selected drivers achieve their strongest recorded results? | Identify all observed seasons tied at each driver’s best points-based rank. |
| Do drivers with a best recorded rank of 1 reach their peak at a different mean age from the other selected drivers? | Compare driver-level peak ages using Welch’s two-sample t-test and a confidence interval. |
| Are early-career results associated with later success? | Compare the first three participation seasons with later seasons using Spearman correlation and permutation tests with Holm correction. |

Pit stops help select the lap-pace sample. A dedicated estimate of their causal impact is not included.

## Data: what we use and where it comes from

The reviewed lap snapshot covers **1996–2026**, with **2026 incomplete**. It contains **639,293 lap timings, 588 observed races, 42 circuit IDs and 149 drivers**. These are observed records, not a guarantee of complete historical coverage.

| Source | Data used | Role in the project |
|---|---|---|
| [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) | Race calendars, driver lap timings, race results, driver birth dates, constructor affiliations and pit stops | Main race and driver data; cached JSON is flattened into CSV tables. |
| [Wikipedia: List of Formula One circuits](https://en.wikipedia.org/wiki/List_of_Formula_One_circuits) | Circuit names, type, direction, length and turn count | Circuit characteristics joined to the lap dataset. |
| [FastF1](https://docs.fastf1.dev/) | Circuit/event metadata and corner coordinates, angles and distances from qualifying sessions | Supplementary circuit-data collection and inspection. These corner features are not used to establish the published pace conclusions. |

Lap records begin in 1996; pit-stop records are used from 2011 onward. Missing earlier pit records mean **unknown**, not “no pit stop.” Wikipedia dimensions come from a snapshot and may not describe every historical layout.

The career notebook initially selects 20 drivers, of whom 15 appear in the available results. Its early/later comparison uses 12 drivers whose debut coverage is available. Partial 2026 is excluded from these career comparisons. This selected cohort is not representative of every F1 driver.

### Data organization

- `data/raw/laps/`: cached lap-timing JSON by season and round.
- `data/raw/results/` and `data/raw/races/`: cached season results and calendars.
- `data/raw/pitstops/`: cached pit-stop responses by season and round.
- `data/raw/lap_times.csv`, `results.csv`, `races.csv`, `pitstops.csv`: flattened analysis inputs.
- `data/raw/wikipedia_circuits_raw.csv`: scraped circuit table.
- `data/raw/fastf1_circuits_raw.csv`, `fastf1_corners_raw.csv`: collected FastF1 metadata.
- `data/processed/`: normalized circuit/corner tables and `laps/lap_times_cleaned.csv`, which includes numeric lap durations.

## What have we found?

| Finding from the reviewed snapshot | What it means |
|---|---|
| Circuit length and absolute lap time: **r = 0.756** | Longer circuits generally take longer to lap. |
| Turn count and seconds per kilometre: **r = 0.087** | Turn count alone shows little linear association with normalized pace. |
| Median absolute teammate gap: **0.611 seconds** | Measurable differences remain within constructors; this is not a pure skill estimate. |
| McLaren’s 2024 median relative pace: **−0.930%** | McLaren leads this descriptive metric; teams have different eligible race samples. |
| Opening race phase: **+1.432%**; final phase: **−0.742%** | Later selected laps are generally faster relative to the driver-race median. Fuel, tyres and strategy are not separated. |
| Welch age comparison: **p = 0.4832** | No statistically significant difference at the 0.05 level; the 95% interval for the mean difference is **−2.179 to +4.317 years**. |
| Early mean rank versus later mean rank: **ρ = 0.5804**, Holm-adjusted permutation **p = 0.1054** | A moderate sample association, but insufficient evidence after correction. |
| Early mean rank versus later best rank: **ρ = 0.1418**, adjusted **p = 0.6596** | Weak sample association; reliable prediction is not established. |

The teammate median uses pace-selected pairs before the additional 5-second gap cutoff used in the season charts. Constructor values describe the combined driver–car–team package. Career ranks are reconstructed from available race points and may differ from official championship standings because Sprint points and official tie-breaks are not included.

A p-value is not the probability that the null hypothesis is true. Failure to reject a null hypothesis does not prove there is no effect. Read the [full findings and definitions](src/result_showcase_website/FINDINGS.md) for selection rules, sample sizes and interpretation.

## Repository guide

```text
f1-driver-vs-car/
├── data/
│   ├── raw/                         # Cached source responses and CSV inputs
│   └── processed/                   # Prepared lap and circuit tables
├── notebooks/                       # Exploratory analysis and statistical findings
├── scripts/
│   ├── fetch/                       # Source-data downloaders
│   ├── build/                       # JSON-to-CSV builders
│   └── *.py                         # Circuit cleaning and inspection
├── src/
│   ├── f1_analysis/api.py           # Shared API/cache utilities
│   └── result_showcase_website/     # Website, figures, evidence, audit and tests
├── requirements.txt                 # Core Python dependencies
└── README.md
```

### Notebooks: recommended reading order

| Notebook | Purpose |
|---|---|
| [00_build_dataset_csvs](notebooks/00_build_dataset_csvs.ipynb) | Entry point for building the lap CSV; its current command needs a path correction before execution. |
| [01_lap_times_eda](notebooks/01_lap_times_eda.ipynb) | Inspect coverage, missing values, duplicates, duration formats, unusual laps and sequence gaps; export numeric durations. |
| [02_lap_performance](notebooks/02_lap_performance.ipynb) | Detailed lap-data integration, pace filtering, circuit comparisons, teammate gaps, constructor pace and race progression. |
| [02_driver_career_eda](notebooks/02_driver_career_eda.ipynb) | A separate career-analysis branch: seasonal ranks, age/experience at peak, early/later outcomes and statistical tests. |
| [03_lap_time_analysis](notebooks/03_lap_time_analysis.ipynb) | Streamlined presentation of the lap-performance findings and limitations. |

The two notebooks numbered `02` address different topics. Notebook `03` summarizes the lap-analysis branch; it is not an independent replication dataset.

### Scripts and shared code

| File | Purpose |
|---|---|
| [fetch_races.py](scripts/fetch/fetch_races.py) | Fetch race calendars and available lap data. |
| [fetch_results.py](scripts/fetch/fetch_results.py) | Fetch season race-result pages. |
| [fetch_pitstops.py](scripts/fetch/fetch_pitstops.py) | Cache pit stops with shared rate limiting and resumable requests. |
| [fetch_fastf1_circuits.py](scripts/fetch/fetch_fastf1_circuits.py) | Collect FastF1 circuit and corner metadata. |
| [fetch_circuits_wiki.py](scripts/fetch/fetch_circuits_wiki.py) | Cache and scrape Wikipedia’s circuit table. |
| [build_dataset_lap_times.py](scripts/build/build_dataset_lap_times.py) | Flatten cached lap responses and validate pagination counts. |
| [build_dataset_races.py](scripts/build/build_dataset_races.py) | Flatten saved calendar snapshots. |
| [build_dataset_results.py](scripts/build/build_dataset_results.py) | Flatten race results and check duplicate records. |
| [build_dataset_pitstops.py](scripts/build/build_dataset_pitstops.py) | Build a pit-stop CSV with duplicate/conflict handling. |
| [build_pitstops.py](scripts/build/build_pitstops.py) | Alternative pit-stop builder with pagination validation and a different output schema. |
| [clean_dataset_cricuit.py](scripts/clean_dataset_cricuit.py) | Normalize and validate Wikipedia circuit data; filename retains its original spelling. |
| [clean_fastf1_circuits.py](scripts/clean_fastf1_circuits.py) | Normalize and deduplicate FastF1 circuit/corner tables. |
| [check_circuit_data.py](scripts/check_circuit_data.py) | Inspect circuit metadata availability through FastF1; this can access the network and write data. |
| [api.py](src/f1_analysis/api.py) | Shared requests, retry handling, pagination, atomic JSON caching and partial-download resume support. |

## Explore or reproduce the analysis

Viewing the website does not require an analysis environment. To work with the notebooks on Linux/WSL, create an environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt numpy scipy seaborn ipykernel jupyterlab
python3 -m jupyterlab
```

Choose that environment as the notebook kernel. Open the career notebook from `notebooks/`, because its root-directory detection assumes that working directory. Read the notebooks and their existing outputs before running cells; some cells write processed files or install packages.

**The current data pipeline needs repairs before an end-to-end rerun.** The [repository audit](src/result_showcase_website/REPOSITORY_AUDIT.md) documents the exact issues, including:

- Incorrect repository-root calculations in several nested scripts.
- Different download and builder directory/filename conventions.
- Notebook 01 exporting `lap_times.csv` while notebooks 02/03 consume `lap_times_cleaned.csv`.
- A mismatch between the Wikipedia scraper’s length field and the cleaner’s expected columns.
- Two pit-stop builders writing different schemas to the same destination.

The stored findings and website can be explored independently of these repairs. Do not assume that running every script in sequence will reproduce the snapshot as currently written. The website is static: changing a CSV does not automatically update its charts or narrative.

## Verification and traceability

From the repository root, run the targeted checks:

```bash
python3 -m unittest discover -s src/result_showcase_website/tests -v
node --check src/result_showcase_website/app.js
node --test src/result_showcase_website/tests/test_site.cjs
```

The Python checks require Python 3.10+ and the existing CSVs/notebooks. They independently reconstruct selected headline results without API calls or dataset writes. The JavaScript checks require Node.js 18+ and verify rendering logic, comparison controls and local links using a DOM fixture. Node is not required to view the website.

All five automated tests pass after redesign integration, including race scrubber and replay checks. Original extracted figure bytes were checked against notebook outputs. Desktop and phone browser checks passed with no reported console warnings or errors. The full 99,999-resample permutation simulation was inspected but not rerun.

Useful reference documents:

- [Findings and answered questions](src/result_showcase_website/FINDINGS.md)
- [File-by-file and notebook claim audit](src/result_showcase_website/REPOSITORY_AUDIT.md)
- [Website setup and implementation](src/result_showcase_website/README.md)
- [Notebook evidence and figure provenance](src/result_showcase_website/evidence/)

## Creators

**Nigel Xherimeja · Sejbi Koromani · Sara Petro**

An independent Formula 1 data-analysis project, not affiliated with Formula 1. Source data and third-party software belong to their respective providers; links above identify their provenance.
