"""
Hidden API Scraper
------------------
Many "JavaScript-only" websites secretly load their data from a JSON API.
Finding that API in DevTools and calling it directly is 10-50x faster than
browser automation — no Selenium, no Playwright, no waiting for rendering.

Demo target: quotes.toscrape.com/js  (data actually comes from /api/quotes)

How the API was found (see README for screenshots):
  1. Open quotes.toscrape.com/js in Chrome
  2. DevTools (F12) -> Network tab -> filter: Fetch/XHR
  3. Reload -> spot the request to /api/quotes?page=1 returning clean JSON
  4. Replicate that request here with `requests` — done.

Usage:
    python api_scraper.py                # scrape all pages via the hidden API
    python api_scraper.py --out-dir out

Compare with browser_scraper.py to see the speed difference.

Author: <your name> | github.com/<your-username>
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests

API_URL = "https://quotes.toscrape.com/api/quotes"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortfolioApiScraper/1.0)",
    "Accept": "application/json",
}
REQUEST_DELAY = 0.3  # the API is light, but stay polite


def scrape_api() -> list[dict]:
    """Walk the paginated JSON API until has_next is false."""
    quotes: list[dict] = []
    page = 1

    while True:
        print(f"Fetching page {page} ...")
        resp = requests.get(API_URL, params={"page": page}, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        for q in data.get("quotes", []):
            quotes.append(
                {
                    "quote": q.get("text", "").strip(),
                    "author": q.get("author", {}).get("name", ""),
                    "tags": ", ".join(q.get("tags", [])),
                }
            )

        if not data.get("has_next"):
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    return quotes


def save_outputs(quotes: list[dict], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "quotes.json"
    json_path.write_text(json.dumps(quotes, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = out_dir / "quotes.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["quote", "author", "tags"])
        writer.writeheader()
        writer.writerows(quotes)

    return json_path, csv_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape via a reverse-engineered hidden API")
    parser.add_argument("--out-dir", default="output", help="output folder")
    args = parser.parse_args()

    start = time.perf_counter()
    try:
        quotes = scrape_api()
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        return 1
    elapsed = time.perf_counter() - start

    json_path, csv_path = save_outputs(quotes, Path(args.out_dir))

    print("\n===== SUMMARY =====")
    print(f"Method        : direct API calls (no browser)")
    print(f"Quotes scraped: {len(quotes)}")
    print(f"Time taken    : {elapsed:.2f} seconds")
    print(f"JSON          : {json_path}")
    print(f"CSV           : {csv_path}")
    print("\nNow run browser_scraper.py and compare the time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
