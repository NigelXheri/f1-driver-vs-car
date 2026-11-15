#!/usr/bin/env python3
"""Clean and validate the Wikipedia Formula 1 circuits dataset."""

import html
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = (
    PROJECT_ROOT / "data" / "raw" / "wikipedia_circuits.csv"
)

PROCESSED_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "wikipedia_circuits_cleaned.csv"
)

TEXT_COLUMNS = [
    "Circuit",
    "Type",
    "Direction",
    "Location",
    "Country",
    "Grands Prix",
    "Season(s)"
]

INTEGER_COLUMNS = [
    "Turns",
    "Grands Prix held"
]

FLOAT_COLUMNS = [
    "Circuit_length_km",
    "Circuit_length_miles"
]

EXPECTED_COLUMNS = TEXT_COLUMNS + INTEGER_COLUMNS + FLOAT_COLUMNS

MISSING_TOKENS = {
    "", "-", "—", "–", "n/a", "na", "nan",
    "none", "null", "?"
}

FOOTNOTE_RE = re.compile(
    r"\s*\[\s*(?:\d+|[a-z]|note\s*\d+)\s*\]",
    re.IGNORECASE
)

KM_TO_MILES = 0.621371


def normalize_text(value):
    """Decode HTML entities and remove formatting artefacts."""
    text = str(value)

    for _ in range(3):
        decoded = html.unescape(text)

        if decoded == text:
            break

        text = decoded

    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("**", "")

    text = FOOTNOTE_RE.sub("", text)

    return " ".join(text.split())


def clean_text(value, column):
    """Clean text values while preserving meaningful information."""
    if pd.isna(value):
        return pd.NA

    text = normalize_text(value)

    if text.lower() in MISSING_TOKENS:
        return pd.NA

    # Remove Wikipedia footnote marker from circuit names.
    if column == "Circuit":
        text = text.replace("†", "").strip()

    return text if text else pd.NA


def clean_column_names(columns):
    """Normalize column names and check for duplicates."""
    cleaned = [normalize_text(column) for column in columns]

    if len(cleaned) != len(set(cleaned)):
        raise ValueError(
            f"Duplicate column names after cleaning: {cleaned}"
        )

    return cleaned


def load_raw(path):
    """Read the original CSV without automatic type conversion."""
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )


def convert_numeric(series, column):
    """Convert a column to numeric and report invalid values."""
    cleaned = series.astype("string").str.strip()

    numbers = pd.to_numeric(cleaned, errors="coerce")

    invalid = cleaned.notna() & numbers.isna()

    if invalid.any():
        details = cleaned[invalid].to_dict()

        raise ValueError(
            f"Invalid numeric values in '{column}': {details}"
        )

    return numbers


def convert_integer(series, column):
    """Convert values to nullable integers without rounding."""
    numbers = convert_numeric(series, column)

    fractional = numbers.notna() & (numbers % 1 != 0)

    if fractional.any():
        raise ValueError(
            f"Non-integer values in '{column}': "
            f"{numbers[fractional].to_dict()}"
        )

    return numbers.astype("Int64")


def clean_dataset(df):
    """Clean the circuits dataset without dropping valid records."""
    df = df.copy()

    # Normalize column names.
    df.columns = clean_column_names(df.columns)

    # Map is not required for the lap time analysis.
    if "Map" in df.columns:
        df = df.drop(columns=["Map"])

    # Check that all required columns exist.
    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}\n"
            f"Available columns: {list(df.columns)}"
        )

    # Clean textual columns.
    for column in TEXT_COLUMNS:
        df[column] = df[column].map(
            lambda value: clean_text(value, column)
        )

    # Convert integer columns.
    for column in INTEGER_COLUMNS:
        df[column] = convert_integer(df[column], column)

    # Convert decimal columns.
    for column in FLOAT_COLUMNS:
        df[column] = convert_numeric(df[column], column).astype(
            "float64"
        )

    # Keep a consistent column order.
    df = df[EXPECTED_COLUMNS]

    return df


def validate_dataset(df):
    """Check dataset quality and print warnings."""
    print("\nDATA VALIDATION")
    print("=" * 60)

    print("\nDataset shape:", df.shape)

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate rows:", df.duplicated().sum())

    print("\nUnique circuits:", df["Circuit"].nunique())

    # Check duplicated circuit names.
    duplicates = df[
        df["Circuit"].duplicated(keep=False)
    ]

    if not duplicates.empty:
        print("\nWARNING: Repeated circuit names:")
        print(duplicates["Circuit"].to_list())

    # Compare circuit lengths in kilometres and miles.
    km = df["Circuit_length_km"]
    miles = df["Circuit_length_miles"]

    difference = (km * KM_TO_MILES - miles).abs()

    mismatch = (
        difference.gt(0.01)
        & km.notna()
        & miles.notna()
    )

    if mismatch.any():
        print("\nWARNING: Circuit length inconsistencies:")
        print(
            df.loc[
                mismatch,
                [
                    "Circuit",
                    "Circuit_length_km",
                    "Circuit_length_miles"
                ]
            ].to_string(index=False)
        )

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))


def main():
    """Execute the cleaning and validation pipeline."""
    if not RAW_PATH.exists():
        print(
            f"ERROR: File not found: {RAW_PATH}",
            file=sys.stderr
        )
        return 1

    print("Reading raw Wikipedia dataset...")

    raw = load_raw(RAW_PATH)

    print("Original shape:", raw.shape)

    try:
        cleaned = clean_dataset(raw)

    except (ValueError, KeyError) as error:
        print(f"\nCLEANING ERROR: {error}", file=sys.stderr)
        return 1

    PROCESSED_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned.to_csv(
        PROCESSED_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\nCLEANING COMPLETED")
    print("=" * 60)

    print("Original rows:", len(raw))
    print("Cleaned rows:", len(cleaned))

    print("Saved to:", PROCESSED_PATH)

    validate_dataset(cleaned)

    return 0


if __name__ == "__main__":
    sys.exit(main())
