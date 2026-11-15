"""Convert cached race results from JSON to a single CSV file."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "results"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "results" / "results.csv"
)

COLUMNS = [
    "season",
    "round",
    "race_name",
    "race_date",
    "circuit_id",
    "driver_id",
    "driver_code",
    "driver_first_name",
    "driver_last_name",
    "driver_date_of_birth",
    "driver_nationality",
    "constructor_id",
    "constructor_name",
    "constructor_nationality",
    "car_number",
    "grid",
    "position",
    "position_text",
    "points",
    "laps_completed",
    "status",
    "race_time",
    "race_time_milliseconds",
    "fastest_lap_rank",
    "fastest_lap_number",
    "fastest_lap_time",
    "fastest_lap_average_speed",
    "fastest_lap_speed_units",
]


def main():
    """Read all season JSON files and export their race results."""
    json_files = sorted(
        path
        for path in INPUT_DIR.glob("*.json")
        if path.stem.isdigit()
    )

    if not json_files:
        raise FileNotFoundError(
            f"No season JSON files found in: {INPUT_DIR}"
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    total_rows = 0
    seen = set()

    with temporary_file.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS)
        writer.writeheader()

        for json_file in json_files:
            pages = json.loads(
                json_file.read_text(encoding="utf-8")
            )

            if not isinstance(pages, list) or not pages:
                raise ValueError(
                    f"Expected a non-empty list of pages: {json_file}"
                )

            expected_total = int(pages[0]["MRData"]["total"])
            file_rows = 0

            for page in pages:
                races = page["MRData"]["RaceTable"]["Races"]

                for race in races:
                    for result in race.get("Results", []):
                        driver = result["Driver"]
                        constructor = result["Constructor"]
                        race_time = result.get("Time", {})
                        fastest_lap = result.get("FastestLap", {})
                        fastest_time = fastest_lap.get("Time", {})
                        speed = fastest_lap.get("AverageSpeed", {})

                        key = (
                            race["season"],
                            race["round"],
                            driver["driverId"],
                        )

                        if key in seen:
                            raise ValueError(
                                f"Duplicate race result: {key}"
                            )
                        seen.add(key)

                        writer.writerow({
                            "season": race["season"],
                            "round": race["round"],
                            "race_name": race["raceName"],
                            "race_date": race["date"],
                            "circuit_id": race["Circuit"]["circuitId"],
                            "driver_id": driver["driverId"],
                            "driver_code": driver.get("code", ""),
                            "driver_first_name": driver.get(
                                "givenName", ""
                            ),
                            "driver_last_name": driver.get(
                                "familyName", ""
                            ),
                            "driver_date_of_birth": driver.get(
                                "dateOfBirth", ""
                            ),
                            "driver_nationality": driver.get(
                                "nationality", ""
                            ),
                            "constructor_id": constructor["constructorId"],
                            "constructor_name": constructor.get("name", ""),
                            "constructor_nationality": constructor.get(
                                "nationality", ""
                            ),
                            "car_number": result.get("number", ""),
                            "grid": result.get("grid", ""),
                            "position": result.get("position", ""),
                            "position_text": result.get("positionText", ""),
                            "points": result.get("points", ""),
                            "laps_completed": result.get("laps", ""),
                            "status": result.get("status", ""),
                            "race_time": race_time.get("time", ""),
                            "race_time_milliseconds": race_time.get(
                                "millis", ""
                            ),
                            "fastest_lap_rank": fastest_lap.get("rank", ""),
                            "fastest_lap_number": fastest_lap.get("lap", ""),
                            "fastest_lap_time": fastest_time.get("time", ""),
                            "fastest_lap_average_speed": speed.get(
                                "speed", ""
                            ),
                            "fastest_lap_speed_units": speed.get(
                                "units", ""
                            ),
                        })

                        file_rows += 1

            if file_rows != expected_total:
                raise ValueError(
                    f"{json_file.name}: expected {expected_total} "
                    f"results, but found {file_rows}."
                )

            total_rows += file_rows
            print(f"{json_file.name}: {file_rows} rows", flush=True)

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nTotal rows: {total_rows}")
    print(f"CSV saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()