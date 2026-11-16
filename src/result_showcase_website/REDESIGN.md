# Science of Speed integration

Integrated on 2026-11-16 from the supplied `science-of-speed-redesign` folder into the existing website directory.

## Project understanding

The repository combines cached Jolpica race/lap/result/pit-stop data with circuit metadata. Python builders and cleaners prepare CSVs; five notebooks explore data quality, circuit associations, teammate gaps, constructor pace, race progression, driver peak ages and early/later career associations. The website publishes a fixed analytical snapshot rather than fetching live results or running a prediction model. The existing audit documents pipeline path/schema issues; the UI migration does not execute or repair those pipelines.

## Preservation map

| Existing result or function | New website location |
| --- | --- |
| 639,293 laps, 588 races, 42 circuits, 149 drivers | Telemetry strip |
| All 10 constructor pace values and eligible race counts | The pace → Constructor pace → exact chart values |
| All 22 signed teammate gaps, counts and constructors | The pace → Teammate gaps → exact chart values |
| 0.611-second gap, pair counts, cutoff and caveats | Typical teammate gap |
| Length/turn correlations and street/permanent comparison | Circuit question and original boxplot |
| All 10 race-phase values and observation counts | Race progression, slider/replay and expandable table |
| All 15 driver peak-age values | The drivers timeline |
| Welch test, confidence interval, hypotheses and limitations | The evidence |
| Both Spearman/permutation/Holm comparisons | The evidence table and comparison strips |
| Selection rules, unresolved questions and causal limits | Under the bodywork |
| All five notebook text extracts, findings and audit | Project archive |
| All 15 unmodified original notebook PNGs | Project archive → All notebook evidence & original figures |

All previous research paragraphs remain in the redesigned page. Replaced material consists of branding, the introduction and decorative car illustration. All numerical arrays and original figure references were compared against the previous Git version. Evidence files, datasets and notebooks were retained.

The supplied folder contained only a favicon in its asset directory, so the repository's existing notebook figures and evidence are essential to this integration. They were not replaced by the incomplete asset folder.

Two inherited figure descriptions were corrected after inspecting the notebook: career cell 38 is mean career year at peak, and cell 43 is the championship career heatmap. The direct heatmap link now opens cell 43. No analytical value was changed.

## Validation

- Three Python evidence tests passed, including independent CSV headline checks and original PNG byte provenance.
- Two JavaScript tests passed, expanded to exercise slider input, replay/stop/completion and point selection alongside the original pace and link checks.
- Both JavaScript files pass syntax checks.
- Local HTTP preview returned 200. Browser interactions were checked at desktop size and a 390 × 844 phone viewport, with no console errors/warnings and no document horizontal overflow on the phone.
- Reduced-motion and print CSS were inspected but not separately browser-tested. The full permutation simulation and data pipeline were not rerun.

## Run locally on Windows

From the repository root:

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory src/result_showcase_website
```

Open http://127.0.0.1:8000 and stop with Ctrl+C. Python 3 is sufficient; no npm install, build or API credentials are needed. You can also open `index.html` directly. If port 8000 is occupied, use 8001 in both the command and URL.
