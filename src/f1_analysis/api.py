"""Download paginated API responses and cache them in one JSON file."""

import json
import shutil
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests


BASE_URL = "https://api.jolpi.ca/ergast/f1"


def save_json(data, file_path):
    """Save JSON atomically to avoid leaving an incomplete final file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = file_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_path.replace(file_path)


def request_page(session, endpoint, offset, *, rate_limiter=None):
    """Request one page, respecting rate limits and retrying failures."""
    url = f"{BASE_URL}/{endpoint.strip('/')}/"

    for attempt in range(6):
        if rate_limiter is None:
            time.sleep(8)
        else:
            rate_limiter.wait()

        try:
            response = session.get(
                url,
                params={"limit": 100, "offset": offset},
                timeout=60,
            )
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 5:
                raise
            print("Connection problem. Retrying...", flush=True)
            time.sleep(10 * (attempt + 1))
            continue

        if response.status_code == 429:
            if rate_limiter is not None:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after)
                except (TypeError, ValueError):
                    try:
                        retry_at = parsedate_to_datetime(retry_after)
                        delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
                    except (TypeError, ValueError):
                        delay = 60
                delay = max(1, delay)
                rate_limiter.defer(delay)
                print(f"Rate limit reached. Pausing requests for {delay:.1f}s.", flush=True)
                continue

            try:
                delay = max(
                    60,
                    float(response.headers.get("Retry-After", "60")),
                )
            except ValueError:
                delay = 60

            print(f"Rate limit reached. Waiting {delay}s.", flush=True)
            time.sleep(delay)
            continue

        if response.status_code >= 500:
            print("Server problem. Retrying...", flush=True)
            time.sleep(10 * (attempt + 1))
            continue

        response.raise_for_status()
        data = response.json()

        if "MRData" not in data:
            raise ValueError("Unexpected API response.")

        return data

    raise RuntimeError(
        f"Download failed: {endpoint}. Run again to resume."
    )


def fetch_all_pages(session, endpoint, output_file, record_type, *, rate_limiter=None):
    """Combine all response pages into one JSON file."""
    output_file = Path(output_file)

    if output_file.exists():
        return json.loads(output_file.read_text(encoding="utf-8"))

    # Keep unfinished pages so interrupted downloads can resume.
    parts_folder = output_file.parent / f"{output_file.stem}_partial"
    parts_folder.mkdir(parents=True, exist_ok=True)

    pages = []
    offset = 0
    expected_total = None

    while True:
        page_file = parts_folder / f"offset_{offset}.json"

        if page_file.exists():
            data = json.loads(page_file.read_text(encoding="utf-8"))
        else:
            data = request_page(session, endpoint, offset, rate_limiter=rate_limiter)
            save_json(data, page_file)

        metadata = data["MRData"]
        races = metadata["RaceTable"]["Races"]
        total = int(metadata["total"])

        if int(metadata["offset"]) != offset:
            raise ValueError("Unexpected pagination offset.")

        if expected_total is None:
            expected_total = total
        elif total != expected_total:
            raise ValueError(f"API total changed: {endpoint}")

        if record_type == "races":
            received = len(races)

        elif record_type == "laps":
            received = sum(
                len(lap["Timings"])
                for race in races
                for lap in race.get("Laps", [])
            )

        elif record_type == "results":
            received = sum(
                len(race.get("Results", []))
                for race in races
            )

        elif record_type == "pitstops":
            received = sum(
                len(race.get("PitStops", []))
                for race in races
            )

        else:
            raise ValueError("Unsupported record type.")

        if received == 0 and offset < total:
            raise ValueError("Unexpected empty page.")

        pages.append(data)
        offset += received

        print(f"{endpoint}: {offset}/{total} records", flush=True)

        if offset >= total:
            if offset != total:
                raise ValueError("Record count does not match API total.")
            break

    save_json(pages, output_file)

    # Remove temporary pages only after the complete file is saved.
    shutil.rmtree(parts_folder)

    return pages
