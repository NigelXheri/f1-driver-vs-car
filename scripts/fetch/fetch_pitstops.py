#!/usr/bin/env python3
"""Cache the raw Jolpica pit-stop response pages for each 2011–2024 round."""

import json
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack
from functools import partial
from pathlib import Path
from queue import SimpleQueue
from threading import Lock

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from f1_analysis.api import fetch_all_pages, request_page, save_json


RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = RAW_DIR / "pitstops"
LEGACY_DIR = RAW_DIR / "api" / "pitstops"
YEARS = range(2011, 2027)
WORKERS = 4


class RateLimiter:
    """Share Jolpica's unauthenticated request budget across the workers."""

    def __init__(self):
        self.lock = Lock()
        self.starts = deque()
        self.resume_at = 0
        self.request_interval = 0.26

    def wait(self):
        while True:
            with self.lock:
                now = time.monotonic()
                while self.starts and now - self.starts[0] >= 3600:
                    self.starts.popleft()

                ready_at = self.resume_at
                if self.starts:
                    ready_at = max(ready_at, self.starts[-1] + self.request_interval)
                if len(self.starts) >= 500:
                    ready_at = max(ready_at, self.starts[0] + 3600)

                delay = ready_at - now
                if delay <= 0:
                    self.starts.append(now)
                    return

            time.sleep(delay)

    def defer(self, delay):
        with self.lock:
            self.resume_at = max(self.resume_at, time.monotonic() + delay)
            # Leave more room for network jitter and shared IP traffic after a 429.
            self.request_interval = min(0.5, self.request_interval * 1.25)


def season_rounds(year, session, rate_limiter):
    calendar = RAW_DIR / "races" / f"{year}.json"
    try:
        pages = json.loads(calendar.read_bytes())
    except FileNotFoundError:
        pages = [request_page(session, f"{year}/races/", 0, rate_limiter=rate_limiter)]

    rounds = {
        int(race["round"])
        for page in pages
        for race in page["MRData"]["RaceTable"]["Races"]
        if int(race["season"]) == year
    }
    if not rounds or len(rounds) != int(pages[0]["MRData"]["total"]):
        raise ValueError(f"Incomplete race calendar for {year}: {calendar}")
    return sorted(rounds)


def read_complete_legacy_page(path, year, round_number):
    """Reuse a legacy response when it contains the entire round."""
    try:
        page = json.loads(path.read_bytes())
        metadata = page["MRData"]
        table = metadata["RaceTable"]
        received = sum(len(race["PitStops"]) for race in table["Races"])
        if (
            int(table["season"]) == year
            and int(table["round"]) == round_number
            and int(metadata["offset"]) == 0
            and received == int(metadata["total"])
        ):
            return page
    except (FileNotFoundError, KeyError, TypeError, ValueError):
        pass
    return None


def cache_round(year, round_number, output_file, sessions, rate_limiter):
    legacy_page = read_complete_legacy_page(
        LEGACY_DIR / output_file.name, year, round_number
    )
    if legacy_page is not None:
        save_json([legacy_page], output_file)
        return

    session = sessions.get()
    try:
        fetch_all_pages(
            session,
            f"{year}/{round_number}/pitstops/",
            output_file,
            "pitstops",
            rate_limiter=rate_limiter,
        )
    finally:
        sessions.put(session)


def main():
    rate_limiter = RateLimiter()
    with requests.Session() as session:
        rounds = [
            (year, round_number, OUTPUT_DIR / f"{year}_round_{round_number}.json")
            for year in YEARS
            for round_number in season_rounds(year, session, rate_limiter)
        ]
    pending = [race for race in rounds if not race[2].is_file()]
    print(f"{len(rounds)} rounds total, {len(pending)} to cache.", flush=True)
    if not pending:
        return

    with ExitStack() as stack:
        sessions = SimpleQueue()
        for _ in range(WORKERS):
            sessions.put(stack.enter_context(requests.Session()))

        download = partial(cache_round, sessions=sessions, rate_limiter=rate_limiter)
        executor = ThreadPoolExecutor(max_workers=WORKERS)
        try:
            futures = [executor.submit(download, *race) for race in pending]
            for future in as_completed(futures):
                future.result()
        finally:
            executor.shutdown(cancel_futures=True)

    print(f"Cached all {len(rounds)} rounds in {OUTPUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
