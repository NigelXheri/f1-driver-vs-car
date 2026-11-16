# The Science of Speed

A local, buildless research showcase for the F1 data-analysis repository. Everything needed by the website is in this directory. No npm packages, CDN, API keys, external fonts, or live API requests are required.

## Open the website

Open `index.html` in a modern browser, or serve this directory from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory src/result_showcase_website
```

Then visit **http://127.0.0.1:8000**. Stop the server with Ctrl+C. On Windows, use `python` instead of `python3` if needed. Python 3 is the only requirement for the optional server. No project data pipeline needs to run.

## Files

- `index.html`: research narrative, accessible sections, statistical explanation, source links, original SVG schematics.
- `styles.css`: responsive black/graphite/navy design with racing-red accents, a light evidence section, mobile layout, reduced-motion and print styles. To add licensed photography, set `--hero-photo:url(assets/your-image.jpg)` on `.hero`.
- `motion.js`: presentation-only layer (scroll reveals, count-ups, tooltips, parallax, hero canvas and a pause control). It holds no research data and the site stays complete without it.
- `app.js`: fixed notebook values, interactive constructor/teammate switch, exact-value tables, career timeline and race-progression charts with a race-distance scrubber, figure gallery. It starts with a Linux Node shebang per project instructions, but is a browser script, not a CLI.
- `assets/`: original schematic favicon and 15 unmodified PNG figures extracted from saved notebook outputs.
- `evidence/`: text extracts of the four displayed analysis notebooks (code, markdown and text outputs), figure provenance, and repository inventory. Cell references are zero-based.
- `REPOSITORY_AUDIT.md`: review findings, file responsibilities, claim verdicts, limitations and verification scope.
- `FINDINGS.md`: persistent project memory: answered questions, definitions, numerical findings, and caveats.
- `tests/test_evidence.py`: read-only verification against the existing CSV snapshot and original notebook images. Uses Python 3.10+ standard library; no API requests or data writes.
- `tests/test_site.cjs`: dependency-free JavaScript rendering/interaction and internal-link checks using a minimal DOM fixture. Requires Node.js 18+.

## Verification

From the repository root:

```bash
python3 -m unittest discover -s src/result_showcase_website/tests -v
node --check src/result_showcase_website/app.js
node --check src/result_showcase_website/motion.js
node --test src/result_showcase_website/tests/test_site.cjs
```

The data assertions intentionally target the reviewed snapshot. If source data changes, investigate changed values rather than changing assertions blindly. Tests do not run notebook cells, download data, or regenerate CSVs. The original scripts remain for the user to run.

The redesign integration passed all three Python evidence checks and both JavaScript tests. The JavaScript checks cover local links, both pace views, exact values, all 15 gallery images, and race scrubbing, replay, stop and completion. JavaScript syntax checks passed for both scripts.

Browser checks covered desktop and a 390 × 844 phone viewport: pace switching, exact-value expansion, keyboard race-distance selection, replay, the statistical table, corrected heatmap link, and the figure gallery. No browser warnings or errors were reported. The phone layout had no document-level horizontal overflow; wide tables scroll within their containers. Reduced-motion and print styles are included but were not separately browser-tested.

All 10 constructors, 22 teammate entries, 15 career entries, 10 phase values/counts and 15 original figure references were compared with the previous website. Numerical arrays are unchanged. Original figure bytes passed the notebook provenance check. Two inherited career-figure labels and the direct heatmap link were corrected. The 99,999-resample permutation simulation was not rerun.

See [REDESIGN.md](REDESIGN.md) for the integration and preservation record.

## Updating the snapshot

Update the source notebooks yourself after resolving the pipeline issues in the audit. Reconcile saved code and outputs, then update numerical arrays in `app.js`, narrative figures in `index.html`, `FINDINGS.md`, evidence extracts and original chart assets together. This site deliberately does not silently regenerate analyses or fetch new race data.

No hosting service is registered and nothing has been published. This is the repository-local deliverable requested by the project owner.

## Readable notebooks

The project archive has four fully clickable notebook cards. **View analysis** opens a static reading page with formatted narrative, tables, saved charts, section navigation and collapsed code. **Download notebook** retrieves a byte-for-byte copy of the original `.ipynb`. Technical sources and the original 15-chart showcase gallery remain in separate expandable sections.

The reading pages preserve all 173 cells and 31 saved PNG figures across the four analysis notebooks. They do not execute Python or fetch external resources. Original notebook wording is retained, including known inconsistencies documented in the claim audit. Notebook downloads require the full repository and its analysis dependencies to run.

The generated HTML, downloads and figure files are included under `notebooks/`, so the normal website command is unchanged. No additional package is needed to view them. Browser verification covered archive-to-reader navigation, section jumps, code expansion, the return-to-archive link and the phone layout; no reader console warnings/errors or phone horizontal overflow were observed.

After editing source notebooks, regenerate from the repository root:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r scripts/build/notebook-requirements.txt
.venv/Scripts/python scripts/build/build_notebook_pages.py
```

The generator reads saved notebook outputs without executing cells and refreshes the four archive cards. Mistune is a build-only Markdown dependency. The reader uses local CSS, native disclosure controls and no JavaScript.

Verify notebook downloads, cell/output coverage, local links and exact saved PNG bytes:

```powershell
python -m unittest discover -s src/result_showcase_website/tests -p test_notebook_pages.py -v
```
