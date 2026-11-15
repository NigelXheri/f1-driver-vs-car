#!/usr/bin/env python3
"""Check circuit information available through FastF1."""

from pathlib import Path

import fastf1
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "fastf1_cache"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.configure(cache_dir=str(CACHE_DIR))


def main():
    """Inspect circuit information across seasons."""
    available_circuits = []

    for year in range(2018, 2025):
        print(f"\nChecking season {year}...")

        try:
            schedule = fastf1.get_event_schedule(year)

            for _, event in schedule.iterrows():
                if pd.isna(event["EventName"]):
                    continue

                event_name = event["EventName"]

                try:
                    session = fastf1.get_session(
                        year,
                        event_name,
                        "Q"
                    )

                    session.load(
                        telemetry=True,
                        laps=True,
                        weather=False,
                        messages=False
                    )

                    circuit = session.get_circuit_info()

                    if circuit is None:
                        print(f"  No circuit data: {event_name}")
                        continue

                    corners = circuit.corners

                    available_circuits.append({
                        "Year": year,
                        "Event": event_name,
                        "CircuitKey": session.session_info[
                            "Meeting"
                        ]["Circuit"]["Key"],
                        "Corners": len(corners),
                        "MarshalLights": len(
                            circuit.marshal_lights
                        ),
                        "MarshalSectors": len(
                            circuit.marshal_sectors
                        ),
                        "Rotation": circuit.rotation,
                        "CornerAnglesAvailable": (
                            corners["Angle"].notna().sum()
                        ),
                        "CornerDistancesAvailable": (
                            corners["Distance"].notna().sum()
                        )
                    })

                    print(
                        f"  OK: {event_name} "
                        f"- {len(corners)} corners"
                    )

                except Exception as error:
                    print(f"  Failed: {event_name} - {error}")

        except Exception as error:
            print(f"Could not load schedule for {year}: {error}")

    df = pd.DataFrame(available_circuits)

    output_file = OUTPUT_DIR / "fastf1_circuit_inventory.csv"
    df.to_csv(output_file, index=False)

    print("\n========== SUMMARY ==========")
    print(f"Total records: {len(df)}")

    if not df.empty:
        print("\nRecords per season:")
        print(df.groupby("Year").size())

        print("\nAvailable columns:")
        print(df.columns.tolist())

    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()
