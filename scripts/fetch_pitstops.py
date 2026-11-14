#!/usr/bin/env python3
"""Fetch Formula 1 pit stops from Jolpica API."""

import json
import time
from pathlib import Path

import requests


BASE_URL = "https://api.jolpi.ca/ergast/f1"

START_YEAR = 2011
END_YEAR = 2026

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "data" / "raw" / "api" / "pitstops"
)


def fetch_pitstops():
    """Download pit stop data for all available races."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_pitstops = 0
    total_races = 0

    for year in range(START_YEAR, END_YEAR + 1):

        print(f"\nDownloading season {year}...")

        round_number = 1

        while True:
            url = (
                f"{BASE_URL}/{year}/"
                f"{round_number}/pitstops.json"
            )

            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 404:
                    break

                response.raise_for_status()

                data = response.json()

                races = data["MRData"]["RaceTable"]["Races"]

                if not races:
                    break

                for race in races:
                    pitstops = race.get("PitStops", [])
                    total_pitstops += len(pitstops)
                    total_races += 1

                output_file = (
                    OUTPUT_DIR
                    / f"{year}_round_{round_number}.json"
                )

                with open(
                    output_file, "w", encoding="utf-8"
                ) as file:
                    json.dump(data, file, indent=4)

                print(
                    f"{year} - Round {round_number}: "
                    f"{len(races[0].get('PitStops', []))} "
                    "pit stops saved"
                )

                round_number += 1
                time.sleep(0.3)

            except requests.RequestException as error:
                print(
                    f"Error in {year}, round "
                    f"{round_number}: {error}"
                )
                break

    print("\nDOWNLOAD COMPLETED")
    print("-------------------------")
    print("Total races:", total_races)
    print("Total pit stops:", total_pitstops)
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    fetch_pitstops()
