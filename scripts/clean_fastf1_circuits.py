#!/usr/bin/env python3
"""Clean and prepare FastF1 circuit and corner datasets."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

RAW_CIRCUITS_FILE = RAW_DIR / "fastf1_circuits_raw.csv"
RAW_CORNERS_FILE = RAW_DIR / "fastf1_corners_raw.csv"

CIRCUITS_OUTPUT = OUTPUT_DIR / "fastf1_circuits.csv"
CORNERS_OUTPUT = OUTPUT_DIR / "fastf1_corners.csv"


def clean_circuits():
    """Clean the circuit-level dataset."""
    df = pd.read_csv(RAW_CIRCUITS_FILE)

    numeric_columns = [
        "Year",
        "Round",
        "CornerCount",
        "Rotation",
        "MarshalLightsCount",
        "MarshalSectorsCount",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["Event"] = df["Event"].astype("string").str.strip()
    df["Country"] = df["Country"].astype("string").str.strip()
    df["Location"] = df["Location"].astype("string").str.strip()

    df = df.dropna(
        subset=["Year", "Event"]
    )

    df = df.drop_duplicates(
        subset=["Year", "Event"],
        keep="last"
    )

    df = df.sort_values(
        ["Year", "Round"]
    )

    df = df.reset_index(drop=True)

    return df


def clean_corners():
    """Clean the corner-level dataset."""
    df = pd.read_csv(RAW_CORNERS_FILE)
    df = df.drop(columns=["CornerLetter"], errors="ignore")

    numeric_columns = [
        "Year",
        "CornerNumber",
        "X",
        "Y",
        "Angle",
        "Distance",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["Event"] = df["Event"].astype("string").str.strip()

    df = df.dropna(
        subset=["Year", "Event", "CornerNumber"]
    )

    df = df.drop_duplicates(
        subset=["Year", "Event", "CornerNumber"],
        keep="last"
    )

    df = df.sort_values(
        ["Year", "Event", "CornerNumber"]
    )

    df = df.reset_index(drop=True)

    return df


def main():
    """Clean and save both FastF1 datasets."""
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not RAW_CIRCUITS_FILE.exists():
        raise FileNotFoundError(
            f"Circuit file not found: {RAW_CIRCUITS_FILE}"
        )

    if not RAW_CORNERS_FILE.exists():
        raise FileNotFoundError(
            f"Corner file not found: {RAW_CORNERS_FILE}"
        )

    circuits = clean_circuits()
    corners = clean_corners()

    circuits.to_csv(
        CIRCUITS_OUTPUT,
        index=False
    )

    corners.to_csv(
        CORNERS_OUTPUT,
        index=False
    )

    print("\n========== CLEANING SUMMARY ==========")

    print("\nCIRCUITS DATASET")
    print(f"Shape: {circuits.shape}")
    print(
        "Duplicates:",
        circuits.duplicated(
            ["Year", "Event"]
        ).sum()
    )
    print(f"Missing values:\n{circuits.isna().sum()}")

    print("\nCORNERS DATASET")
    print(f"Shape: {corners.shape}")
    print(
        "Duplicates:",
        corners.duplicated(
            ["Year", "Event", "CornerNumber"]
        ).sum()
    )
    print(f"Missing values:\n{corners.isna().sum()}")

    print("\nRECORDS PER SEASON")
    print(circuits.groupby("Year").size())

    print("\nSAVED FILES")
    print(CIRCUITS_OUTPUT)
    print(CORNERS_OUTPUT)


if __name__ == "__main__":
    main()
