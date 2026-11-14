#!/usr/bin/env python3
"""Scrape Formula One circuits from Wikipedia."""

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup


URL = "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits"

HEADERS = {
    "User-Agent": "Formula1StudentProject/1.0 (student project)"
}

RAW_FILE = "data/raw/wikipedia_circuits.html"
RAW_CSV_FILE = "data/raw/wikipedia_circuits.csv"


def save_html(html):
    """Save the original Wikipedia HTML page."""
    with open(RAW_FILE, "w", encoding="utf-8") as file:
        file.write(html)


def get_html():
    """Read the saved HTML or download it if it does not exist."""
    if os.path.exists(RAW_FILE):
        with open(RAW_FILE, "r", encoding="utf-8") as file:
            return file.read()

    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    html = response.text
    save_html(html)

    return html


def scrape_circuits(html):
    """Extract circuit information from the Wikipedia table."""
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table", class_="wikitable")

    target_table = None

    for table in tables:
        first_row = table.find("tr")

        if first_row is None:
            continue

        headers = [
            cell.get_text(" ", strip=True)
            for cell in first_row.find_all(["th", "td"])
        ]

        if "Circuit" in headers and "Type" in headers:
            target_table = table
            break

    if target_table is None:
        raise ValueError("Formula One circuits table not found.")

    rows = target_table.find_all("tr")

    column_names = [
        cell.get_text(" ", strip=True)
        for cell in rows[0].find_all(["th", "td"])
    ]

    circuits = []

    for row in rows[1:]:
        cells = row.find_all(["th", "td"])

        if len(cells) != len(column_names):
            continue

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        circuit = dict(zip(column_names, values))
        circuits.append(circuit)

    return circuits


def main():
    """Run the Wikipedia scraping process."""
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    html = get_html()
    circuits = scrape_circuits(html)

    df = pd.DataFrame(circuits)

    df.to_csv(RAW_CSV_FILE, index=False)

    print("Scraping completed successfully!")
    print("Total circuits:", len(df))
    print("Total columns:", len(df.columns))
    print("Raw CSV saved to:", RAW_CSV_FILE)

    print("\nFirst 5 circuits:")
    print(df.head())


if __name__ == "__main__":
    main()
