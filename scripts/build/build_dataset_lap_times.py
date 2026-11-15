#!/usr/bin/env python3
"""Flatten cached Jolpica lap timing pages into one CSV."""

import argparse
import csv
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "laps"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "lap_times.csv"
RACE_FILENAME = re.compile(r"([0-9]{4})_round_([0-9]+)\.json")
COLUMNS = (
    "season", "round", "race_name", "race_date", "race_start_time",
    # "race_url",
    "circuit_id", "circuit_name",
    # "circuit_url",
    # "country", "locality",
    # "latitude", "longitude",
    "driver_id", "lap", "position", "lap_time",
)


def write_race(csv_writer, path):
    pages = json.loads(path.read_bytes())
    expected = int(pages[0]["MRData"]["total"])
    count = 0

    for page in pages:
        metadata = page["MRData"]
        if int(metadata["offset"]) != count or int(metadata["total"]) != expected:
            raise ValueError(f"{path.name}: inconsistent page offset or total")

        for race in metadata["RaceTable"]["Races"]:
            circuit = race["Circuit"]
            location = circuit.get("Location", {})
            race_fields = (
                race["season"], race["round"], race["raceName"], race["date"],
                race.get("time", ""), 
                # race.get("url", ""), 
                circuit["circuitId"],
                circuit["circuitName"],
                # circuit.get("url", ""),
                # location.get("country", ""),
                # location.get("locality", ""),
                # location.get("lat", ""), location.get("long", ""),
            )
            for lap in race.get("Laps", []):
                for timing in lap["Timings"]:
                    csv_writer.writerow((
                        *race_fields, timing["driverId"], lap["number"],
                        timing.get("position", ""), timing["time"],
                    ))
                    count += 1

    if count != expected:
        raise ValueError(f"{path.name}: expected {expected} timings, found {count}")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE, help="CSV output path")
    parser.add_argument("--limit", type=int, help="Process only the first N rounds")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    rounds = []
    for path in INPUT_DIR.glob("*.json"):
        match = RACE_FILENAME.fullmatch(path.name)
        if match:
            year, round_number = map(int, match.groups())
            rounds.append((year, round_number, path))
    rounds.sort()
    rounds = rounds[:args.limit]
    if not rounds:
        raise FileNotFoundError(f"No race JSON files found in {INPUT_DIR}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output = NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", suffix=".tmp",
        dir=args.output.parent, delete=False,
    )
    temporary_path = Path(output.name)
    try:
        with output:
            csv_writer = csv.writer(output)
            csv_writer.writerow(COLUMNS)
            count = sum(write_race(csv_writer, path) for _, _, path in rounds)
        temporary_path.replace(args.output)
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Wrote {count:,} lap timings from {len(rounds):,} rounds to {args.output}")


if __name__ == "__main__":
    main()
