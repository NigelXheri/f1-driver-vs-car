"""Download race results and save one JSON file per season."""

import sys
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from f1_analysis.api import fetch_all_pages


START_YEAR = 1996
END_YEAR = 2026
CONTACT_EMAIL = "sara.petro.tech@gmail.com"

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "results"


def main():
    """Download and cache all result pages for each season."""
    if CONTACT_EMAIL == "YOUR_EMAIL_HERE":
        raise ValueError("Replace YOUR_EMAIL_HERE with your contact email.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": (
                f"F1AnalysisStudentProject/1.0 "
                f"(contact: {CONTACT_EMAIL})"
            )
        })

        for season in range(START_YEAR, END_YEAR + 1):
            print(f"\nProcessing season {season}...", flush=True)

            output_file = OUTPUT_DIR / f"{season}.json"

            pages = fetch_all_pages(
                session=session,
                endpoint=f"{season}/results/",
                output_file=output_file,
                record_type="results",
            )

            total_results = sum(
                len(race.get("Results", []))
                for page in pages
                for race in page["MRData"]["RaceTable"]["Races"]
            )

            print(
                f"Season {season}: {total_results} results.",
                flush=True,
            )
            print(f"File saved at: {output_file}", flush=True)

    print("\nAll requested seasons are saved.")


if __name__ == "__main__":
    main()