"""Download available lap data from 1996 to the current year."""

import sys
from datetime import date
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from f1_analysis.api import fetch_all_pages


START_YEAR = 1996
DOWNLOAD_DATE = date.today()
END_YEAR = DOWNLOAD_DATE.year
CONTACT_EMAIL = "sara.petro.tech@gmail.com"

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
LAPS_FOLDER = RAW_FOLDER / "laps"
RACES_FOLDER = RAW_FOLDER / "races" / DOWNLOAD_DATE.isoformat()


def main():
    """Download calendars and save one complete JSON per race."""
    if CONTACT_EMAIL == "YOUR_EMAIL":
        raise ValueError("Replace YOUR_EMAIL before running.")

    RAW_FOLDER.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": (
                f"F1LapTimeAnalysis/1.0 (contact: {CONTACT_EMAIL})"
            )
        })

        for season in range(START_YEAR, END_YEAR + 1):
            calendar_pages = fetch_all_pages(
                session=session,
                endpoint=f"{season}/races",
                output_file=RACES_FOLDER / f"{season}.json",
                record_type="races",
            )

            races = [
                race
                for page in calendar_pages
                for race in page["MRData"]["RaceTable"]["Races"]
            ]
            races.sort(key=lambda race: int(race["round"]))

            for race in races:
                race_date = date.fromisoformat(race["date"])

                # Exclude today's races and future races.
                if race_date >= DOWNLOAD_DATE:
                    continue

                round_number = int(race["round"])
                output_file = (
                    LAPS_FOLDER
                    / str(season)
                    / f"round_{round_number:02d}.json"
                )

                print(
                    f"\n{season} | Round {round_number} | "
                    f"{race['raceName']}",
                    flush=True,
                )

                fetch_all_pages(
                    session=session,
                    endpoint=f"{season}/{round_number}/laps",
                    output_file=output_file,
                    record_type="laps",
                )

    print(f"\nDownload completed: {LAPS_FOLDER}")


if __name__ == "__main__":
    main()