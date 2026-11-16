# Driver / Machine

A local, buildless research showcase for the F1 driver-vs-car repository. Everything needed by the website is in this directory. No npm packages, CDN, API keys, external fonts, or live API requests are required.

## Open the website

Open `index.html` in a modern browser, or serve this directory from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory src/result_showcase_website
```

Then visit **http://127.0.0.1:8000**. Stop the server with Ctrl+C. On Windows, use `python` instead of `python3` if needed. Python 3 is the only requirement for the optional server. No project data pipeline needs to run.

## Files

- `index.html`: research narrative, accessible sections, statistical explanation, source links, original SVG schematics.
- `styles.css`: responsive charcoal/red/neutral design, mobile layout, reduced-motion and print styles.
- `app.js`: fixed notebook values, interactive constructor/teammate switch, exact-value tables, career and progression charts, figure gallery. It starts with a Linux Node shebang per project instructions, but is a browser script, not a CLI.
- `assets/`: original schematic favicon and 15 unmodified PNG figures extracted from saved notebook outputs.
- `evidence/`: complete text extracts of all five notebooks (code, markdown and text outputs), figure provenance, and repository inventory. Cell references are zero-based.
- `REPOSITORY_AUDIT.md`: review findings, file responsibilities, claim verdicts, limitations and verification scope.
- `FINDINGS.md`: persistent project memory: answered questions, definitions, numerical findings, and caveats.
- `tests/test_evidence.py`: read-only verification against the existing CSV snapshot and original notebook images. Uses Python 3.10+ standard library; no API requests or data writes.
- `tests/test_site.cjs`: dependency-free JavaScript rendering/interaction and internal-link checks using a minimal DOM fixture. Requires Node.js 18+.

## Verification

From the repository root:

```bash
python3 -m unittest discover -s src/result_showcase_website/tests -v
node --check src/result_showcase_website/app.js
node --test src/result_showcase_website/tests/test_site.cjs
```

The data assertions intentionally target the reviewed snapshot. If source data changes, investigate changed values rather than changing assertions blindly. Tests do not run notebook cells, download data, or regenerate CSVs. The original scripts remain for the user to run.

The review reproduced selected headline statistics independently from CSVs, checked the saved permutation outputs and Holm arithmetic, and preserved original plot bytes. The 99,999-resample SciPy permutation procedure was inspected but not rerun. It needs SciPy and NumPy, absent from the host Python environment. Browser preview was blocked by the available browser tool's local-file protocol policy; visual rendering and real-browser interaction have not been verified. The site includes responsive CSS, but mobile rendering remains to be checked in a browser.

## Updating the snapshot

Update the source notebooks yourself after resolving the pipeline issues in the audit. Reconcile saved code and outputs, then update numerical arrays in `app.js`, narrative figures in `index.html`, `FINDINGS.md`, evidence extracts and original chart assets together. This site deliberately does not silently regenerate analyses or fetch new race data.

No hosting service is registered and nothing has been published. This is the repository-local deliverable requested by the project owner.
