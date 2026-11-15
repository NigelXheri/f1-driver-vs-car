#!/usr/bin/env python3
"""Build a CSV with one row per pit stop from cached Jolpica responses."""

import csv
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pitstops"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "pitstops.csv"
ROUND_FILENAME = re.compile(r"([0-9]{4})_round_([0-9]+)\.json")
COLUMNS = (
    "season", "round", "race_name", "race_date", "race_start_time",
    "circuit_id", "circuit_name", "driver_id", "lap", "stop",
    "pit_stop_time", "duration",
)


def write_round(writer, path):
    """Write all pages for one round and check the reported record count."""
    pages = json.loads(path.read_bytes())
    if isinstance(pages, dict):
        pages = [pages]
    if not pages:
        raise ValueError(f"{path.name}: no response pages")

    expected = int(pages[0]["MRData"]["total"])
    count = 0
    for page in pages:
        metadata = page["MRData"]
        if int(metadata["offset"]) != count or int(metadata["total"]) != expected:
            raise ValueError(f"{path.name}: inconsistent page offset or total")

        for race in metadata["RaceTable"]["Races"]:
            circuit = race["Circuit"]
            race_fields = (
                race["season"], race["round"], race["raceName"], race["date"],
                race.get("time", ""), circuit["circuitId"], circuit["circuitName"],
            )
            for stop in race["PitStops"]:
                writer.writerow((
                    *race_fields, stop["driverId"], stop.get("lap", ""),
                    stop.get("stop", ""), stop.get("time", ""),
                    stop.get("duration", ""),
                ))
                count += 1

    if count != expected:
        raise ValueError(f"{path.name}: expected {expected} pit stops, found {count}")
    return count


def main():
    rounds = []
    for path in INPUT_DIR.glob("*.json"):
        match = ROUND_FILENAME.fullmatch(path.name)
        if match:
            season, round_number = map(int, match.groups())
            rounds.append((season, round_number, path))
    if not rounds:
        raise FileNotFoundError(f"No pit-stop JSON files found in {INPUT_DIR}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", suffix=".tmp",
        dir=OUTPUT_FILE.parent, delete=False,
    )
    temporary_path = Path(output.name)
    try:
        with output:
            writer = csv.writer(output)
            writer.writerow(COLUMNS)
            count = sum(write_round(writer, path) for _, _, path in sorted(rounds))
        temporary_path.replace(OUTPUT_FILE)
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Wrote {count:,} pit stops from {len(rounds):,} rounds to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
