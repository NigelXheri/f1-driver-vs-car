"""Convert cached pit-stop API responses into one CSV file."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pitstops"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "pitstops.csv"

COLUMNS = [
    "season",
    "round",
    "race_name",
    "race_date",
    "circuit_id",
    "driver_id",
    "stop",
    "lap",
    "pit_time",
    "pit_duration",
]


def main():
    """Read cached JSON files and export one row per pit stop."""
    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in: {INPUT_DIR}"
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    seen = {}
    total_rows = 0
    duplicate_rows = 0

    with temporary_file.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS)
        writer.writeheader()

        for json_file in json_files:
            data = json.loads(
                json_file.read_text(encoding="utf-8")
            )

            pages = data if isinstance(data, list) else [data]
            file_rows = 0

            for page in pages:
                if not isinstance(page, dict) or "MRData" not in page:
                    raise ValueError(
                        f"Unsupported JSON structure: {json_file.name}"
                    )

                races = page["MRData"]["RaceTable"]["Races"]

                for race in races:
                    for pitstop in race.get("PitStops", []):
                        row = {
                            "season": int(race["season"]),
                            "round": int(race["round"]),
                            "race_name": race.get("raceName", ""),
                            "race_date": race.get("date", ""),
                            "circuit_id": race.get(
                                "Circuit", {}
                            ).get("circuitId", ""),
                            "driver_id": pitstop["driverId"],
                            "stop": int(pitstop["stop"]),
                            "lap": int(pitstop["lap"]),
                            "pit_time": pitstop.get("time", ""),
                            "pit_duration": pitstop.get("duration", ""),
                        }

                        key = (
                            row["season"],
                            row["round"],
                            row["driver_id"],
                            row["stop"],
                        )

                        if key in seen:
                            if seen[key] != row:
                                raise ValueError(
                                    f"Conflicting pit-stop records: {key}"
                                )
                            duplicate_rows += 1
                            continue

                        seen[key] = row
                        writer.writerow(row)
                        file_rows += 1

            total_rows += file_rows
            print(
                f"{json_file.name}: {file_rows} rows added",
                flush=True,
            )

    if total_rows == 0:
        raise ValueError(
            "No pit-stop records found. Check the JSON structure."
        )

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nTotal pit stops: {total_rows:,}")
    print(f"Identical duplicates skipped: {duplicate_rows:,}")
    print(f"CSV saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()