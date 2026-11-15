# f1-driver-vs-car
Comparing Formula 1 teammates across 75 years of race results to see how often one consistently finishes ahead and whether the gap varies by circuit type and length.

## File descriptions

### `scripts/`

Runnable scripts for downloading source data and building analysis-ready CSVs.

| File | Purpose |
| --- | --- |
| [`fetch_data.py`](scripts/fetch_data.py) | Downloads Jolpica race calendars and lap times from 1996 through the current season. Saves dated calendar snapshots and one lap-time JSON file per past round. |
| [`fetch_results.py`](scripts/fetch_results.py) | Downloads Jolpica race results for 1996–2026 and saves one JSON file per season in `data/raw/results/`. |
| [`fetch_pitstops.py`](scripts/fetch_pitstops.py) | Caches Jolpica pit-stop response pages for every round from 2011–2024 in `data/raw/pitstops/`, using filenames such as `2024_round_24.json`. |
| [`wikipedia_circuit.py`](scripts/wikipedia_circuit.py) | Scrapes Wikipedia’s list of Formula One circuits and saves the source HTML and an extracted CSV in `data/raw/`. |
| [`clean_dataset_cricuit.py`](scripts/clean_dataset_cricuit.py) | Normalizes and validates the raw Wikipedia circuit CSV, then writes `data/processed/wikipedia_circuits_cleaned.csv`. |
| [`build_dataset_laps.py`](scripts/build_dataset_laps.py) | Converts cached lap-time JSON files into `data/processed/laps/lap_times.csv`. |
| [`build_dataset_races.py`](scripts/build_dataset_races.py) | Uses the latest dated calendar snapshot for each season to build `data/processed/races/races.csv`. |
| [`build_dataset_results.py`](scripts/build_dataset_results.py) | Combines the cached season results into `data/processed/results/results.csv`, with one row per driver per race. |

### `src/`

Contains `f1_analysis/`, the Python package for code shared across scripts.

| File | Purpose |
| --- | --- |
| [`f1_analysis/__init__.py`](src/f1_analysis/__init__.py) | Marks `f1_analysis` as a Python package. |
| [`f1_analysis/api.py`](src/f1_analysis/api.py) | Provides shared Jolpica request, retry, pagination, and JSON caching helpers. It also saves partial downloads so they can resume. |
| [`f1_analysis/processing.py`](src/f1_analysis/processing.py) | Empty placeholder for data processing. |
| [`f1_analysis/scraping.py`](src/f1_analysis/scraping.py) | Empty placeholder for scraping. |
| [`f1_analysis/statistics.py`](src/f1_analysis/statistics.py) | Empty placeholder for statistical analysis. |
| [`f1_analysis/visualization.py`](src/f1_analysis/visualization.py) | Empty placeholder for visualization. |
