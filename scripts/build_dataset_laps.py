"""Convert cached lap JSON files into one CSV dataset."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FOLDER = PROJECT_ROOT / "data" / "raw" / "laps"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "laps" / "lap_times.csv"

COLUMNS = [
    "season",
    "round",
    "race_name",
    "race_date",
    "race_start_time",
    "race_url",
    "circuit_id",
    "circuit_name",
    "circuit_url",
    "country",
    "locality",
    "latitude",
    "longitude",
    "driver_id",
    "lap",
    "position",
    "lap_time",
]


def main():
    """Flatten all completed race files and save their lap records."""
    files = sorted(INPUT_FOLDER.glob("*/round_*.json"))

    if not files:
        raise FileNotFoundError(
            f"No completed race JSON files found in {INPUT_FOLDER}"
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")
    total_rows = 0

    with temporary_file.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS)
        writer.writeheader()

        for file_path in files:
            pages = json.loads(file_path.read_text(encoding="utf-8"))
            file_rows = 0

            for page in pages:
                races = page["MRData"]["RaceTable"]["Races"]

                for race in races:
                    circuit = race["Circuit"]
                    location = circuit.get("Location", {})

                    race_info = {
                        "season": race["season"],
                        "round": race["round"],
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
                    }

                    for lap in race.get("Laps", []):
                        for timing in lap["Timings"]:
                            writer.writerow({
                                **race_info,
                                "driver_id": timing["driverId"],
                                "lap": lap["number"],
                                "position": timing.get("position", ""),
                                "lap_time": timing["time"],
                            })
                            file_rows += 1

            expected_rows = int(pages[0]["MRData"]["total"])

            if file_rows != expected_rows:
                raise ValueError(
                    f"{file_path.name}: expected {expected_rows} "
                    f"records, found {file_rows}"
                )

            total_rows += file_rows
            print(
                f"{file_path.parent.name}/{file_path.name}: "
                f"{file_rows} rows"
            )

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nRace files processed: {len(files)}")
    print(f"Total rows: {total_rows}")
    print(f"CSV size: {OUTPUT_FILE.stat().st_size / (1024 ** 2):.2f} MiB")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
