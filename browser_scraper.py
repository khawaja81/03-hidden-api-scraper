"""
Browser Scraper (comparison baseline)
-------------------------------------
Scrapes the SAME data as api_scraper.py, but the "obvious" way: a real
browser via Playwright, rendering JavaScript and clicking through pages.

Purpose: run both scripts and compare the timing. On a typical connection
the hidden-API method finishes in ~2-4 seconds; this one takes 30-60+.
That difference is why reverse-engineering APIs matters on client projects.

Setup (one time):
    pip install playwright
    playwright install chromium

Usage:
    python browser_scraper.py

Author: <your name> | github.com/<your-username>
"""

import sys
import time

from playwright.sync_api import sync_playwright

START_URL = "https://quotes.toscrape.com/js/"


def scrape_with_browser() -> list[dict]:
    quotes: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(START_URL, timeout=30000)

        page_num = 1
        while True:
            page.wait_for_selector("div.quote", timeout=15000)
            print(f"Rendering page {page_num} ...")

            for card in page.query_selector_all("div.quote"):
                text_el = card.query_selector("span.text")
                author_el = card.query_selector("small.author")
                tag_els = card.query_selector_all("a.tag")
                quotes.append(
                    {
                        "quote": text_el.inner_text().strip() if text_el else "",
                        "author": author_el.inner_text().strip() if author_el else "",
                        "tags": ", ".join(t.inner_text() for t in tag_els),
                    }
                )

            next_link = page.query_selector("li.next a")
            if not next_link:
                break
            next_link.click()
            page.wait_for_load_state("domcontentloaded")
            page_num += 1

        browser.close()

    return quotes


def main() -> int:
    start = time.perf_counter()
    quotes = scrape_with_browser()
    elapsed = time.perf_counter() - start

    print("\n===== SUMMARY =====")
    print(f"Method        : full browser automation (Playwright)")
    print(f"Quotes scraped: {len(quotes)}")
    print(f"Time taken    : {elapsed:.2f} seconds")
    print("\nCompare this time with api_scraper.py — same data, different method.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
