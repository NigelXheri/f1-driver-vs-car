#!/usr/bin/env python3
"""Fetch Formula 1 circuit and corner data using FastF1."""

from datetime import date
from pathlib import Path

import fastf1
import pandas as pd
from fastf1.exceptions import RateLimitExceededError


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CACHE_DIR = RAW_DIR / "fastf1_cache"

CIRCUITS_FILE = RAW_DIR / "fastf1_circuits_raw.csv"
CORNERS_FILE = RAW_DIR / "fastf1_corners_raw.csv"

START_YEAR = 2018
END_YEAR = date.today().year

CIRCUIT_COLUMNS = [
    "Year",
    "Round",
    "Event",
    "Country",
    "Location",
    "CircuitKey",
    "CornerCount",
    "Rotation",
    "MarshalLightsCount",
    "MarshalSectorsCount",
]

CORNER_COLUMNS = [
    "Year",
    "Event",
    "CornerNumber",
    "CornerLetter",
    "X",
    "Y",
    "Angle",
    "Distance",
]


def configure_fastf1():
    """Configure FastF1 cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    fastf1.Cache.configure(cache_dir=str(CACHE_DIR))


def load_existing_data():
    """Load previously collected circuit and corner data."""
    if CIRCUITS_FILE.exists():
        circuits = pd.read_csv(CIRCUITS_FILE)
    else:
        circuits = pd.DataFrame(columns=CIRCUIT_COLUMNS)

    if CORNERS_FILE.exists():
        corners = pd.read_csv(CORNERS_FILE)
    else:
        corners = pd.DataFrame(columns=CORNER_COLUMNS)

    return circuits, corners


def save_data(circuits, corners):
    """Save collected data to raw CSV files."""
    circuits.to_csv(CIRCUITS_FILE, index=False)
    corners.to_csv(CORNERS_FILE, index=False)


def event_is_complete(circuits, corners, year, event_name):
    """Check whether all corner data for an event already exists."""
    event_circuit = circuits[
        (circuits["Year"] == year)
        & (circuits["Event"] == event_name)
    ]

    event_corners = corners[
        (corners["Year"] == year)
        & (corners["Event"] == event_name)
    ]

    if event_circuit.empty:
        return False

    expected = pd.to_numeric(
        event_circuit.iloc[-1]["CornerCount"],
        errors="coerce"
    )

    actual = len(event_corners)

    if pd.isna(expected):
        return False

    return actual >= expected


def fetch_event(year, event):
    """Fetch circuit and corner information for one event."""
    event_name = event["EventName"]

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
        print(f"  No circuit information: {event_name}")
        return None, None

    meeting = session.session_info.get("Meeting", {})
    circuit_info = meeting.get("Circuit", {})

    circuit_record = {
        "Year": year,
        "Round": event["RoundNumber"],
        "Event": event_name,
        "Country": event["Country"],
        "Location": event["Location"],
        "CircuitKey": circuit_info.get("Key"),
        "CornerCount": len(circuit.corners),
        "Rotation": circuit.rotation,
        "MarshalLightsCount": len(circuit.marshal_lights),
        "MarshalSectorsCount": len(circuit.marshal_sectors),
    }

    corner_records = []

    for _, corner in circuit.corners.iterrows():
        corner_records.append({
            "Year": year,
            "Event": event_name,
            "CornerNumber": corner["Number"],
            "CornerLetter": corner["Letter"],
            "X": corner["X"],
            "Y": corner["Y"],
            "Angle": corner["Angle"],
            "Distance": corner["Distance"],
        })

    return circuit_record, corner_records


def main():
    """Collect circuit and corner data from 2018 to the current year."""
    configure_fastf1()

    circuits, corners = load_existing_data()

    print("\n========== FASTF1 DATA COLLECTION ==========")
    print(f"Start year: {START_YEAR}")
    print(f"End year: {END_YEAR}")
    print(f"Existing circuit records: {len(circuits)}")
    print(f"Existing corner records: {len(corners)}")

    today = pd.Timestamp.today().normalize()
    stop_collection = False

    for year in range(START_YEAR, END_YEAR + 1):
        print(f"\n========== SEASON {year} ==========")

        try:
            schedule = fastf1.get_event_schedule(
                year,
                include_testing=False
            )

        except RateLimitExceededError as error:
            print(f"\nRATE LIMIT REACHED: {error}")
            print("Stopping collection. Run again later.")
            break

        except Exception as error:
            print(f"Could not load schedule for {year}: {error}")
            continue

        for _, event in schedule.iterrows():
            event_name = event["EventName"]

            if pd.isna(event_name):
                continue

            event_date = pd.to_datetime(
                event["EventDate"],
                errors="coerce"
            )

            if pd.notna(event_date) and event_date.normalize() > today:
                print(f"  Skipping future event: {event_name}")
                continue

            if event_is_complete(
                circuits,
                corners,
                year,
                event_name
            ):
                print(f"  Already collected: {event_name}")
                continue

            print(f"\nFetching: {event_name}")

            try:
                circuit_record, corner_records = fetch_event(
                    year,
                    event
                )

                if circuit_record is None:
                    continue

                circuits = circuits[
                    ~(
                        (circuits["Year"] == year)
                        & (circuits["Event"] == event_name)
                    )
                ]

                corners = corners[
                    ~(
                        (corners["Year"] == year)
                        & (corners["Event"] == event_name)
                    )
                ]

                circuits = pd.concat(
                    [
                        circuits,
                        pd.DataFrame([circuit_record])
                    ],
                    ignore_index=True
                )

                if corner_records:
                    corners = pd.concat(
                        [
                            corners,
                            pd.DataFrame(corner_records)
                        ],
                        ignore_index=True
                    )

                circuits = circuits.reindex(
                    columns=CIRCUIT_COLUMNS
                )

                corners = corners.reindex(
                    columns=CORNER_COLUMNS
                )

                save_data(circuits, corners)

                print(
                    f"  Saved: {event_name} "
                    f"- {len(corner_records)} corners"
                )

            except RateLimitExceededError as error:
                print(f"\nRATE LIMIT REACHED: {error}")
                print("Stopping collection. Run again later.")
                stop_collection = True
                break

            except Exception as error:
                print(f"  Failed: {event_name} - {error}")
                continue

        if stop_collection:
            break

    save_data(circuits, corners)

    print("\n========== COLLECTION SUMMARY ==========")
    print(f"Total circuit records: {len(circuits)}")
    print(f"Total corner records: {len(corners)}")

    if not circuits.empty:
        print("\nRecords per season:")
        print(circuits.groupby("Year").size())

    print("\nSaved files:")
    print(CIRCUITS_FILE)
    print(CORNERS_FILE)


if __name__ == "__main__":
    main()
