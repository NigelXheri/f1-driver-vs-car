"""Convert cached race calendars into a CSV dataset."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FOLDER = PROJECT_ROOT / "data" / "raw" / "races"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "races" / "races.csv"
)

COLUMNS = [
    "season", "round", "race_name", "race_date",
    "race_start_time", "race_url", "circuit_id",
    "circuit_name", "circuit_url", "country",
    "locality", "latitude", "longitude",
]


def main():
    """Export the latest saved calendar for each season."""
    if not INPUT_FOLDER.exists():
        raise FileNotFoundError(f"Folder not found: {INPUT_FOLDER}")

    season_files = {}

    # Use the latest dated snapshot available for each season.
    for snapshot_folder in sorted(INPUT_FOLDER.iterdir()):
        if snapshot_folder.is_dir():
            for file_path in sorted(snapshot_folder.glob("*.json")):
                if file_path.stem.isdigit():
                    season_files[int(file_path.stem)] = file_path

    if not season_files:
        raise FileNotFoundError("No saved race calendars found.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    total_rows = 0
    seen_races = set()

    with temporary_file.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS)
        writer.writeheader()

        for season, file_path in sorted(season_files.items()):
            pages = json.loads(file_path.read_text(encoding="utf-8"))

            races = [
                race
                for page in pages
                for race in page["MRData"]["RaceTable"]["Races"]
            ]

            expected = int(pages[0]["MRData"]["total"])
            if len(races) != expected:
                raise ValueError(f"Incomplete calendar for {season}.")

            races.sort(key=lambda race: int(race["round"]))

            for race in races:
                key = (int(race["season"]), int(race["round"]))

                if key in seen_races:
                    raise ValueError(f"Duplicate race: {key}")

                seen_races.add(key)

                circuit = race["Circuit"]
                location = circuit.get("Location", {})

                writer.writerow({
                    "season": key[0],
                    "round": key[1],
                    "race_name": race["raceName"],
                    "race_date": race["date"],
                    "race_start_time": race.get("time", ""),
                    "race_url": race.get("url", ""),
                    "circuit_id": circuit["circuitId"],
                    "circuit_name": circuit["circuitName"],
                    "circuit_url": circuit.get("url", ""),
                    "country": location.get("country", ""),
                    "locality": location.get("locality", ""),
                    "latitude": location.get("lat", ""),
                    "longitude": location.get("long", ""),
                })

                total_rows += 1

            print(f"Season {season}: {len(races)} races")

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nTotal rows: {total_rows}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()