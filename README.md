# Hidden API Scraper — 10-50x Faster Than Browser Automation

Many "JavaScript-heavy" sites don't need Selenium or Playwright at all — their frontend quietly loads data from a **JSON API**. This project shows how I find that API in Chrome DevTools and call it directly.

**Same site, same data, two methods:**

| Method | Script | Typical time |
|---|---|---|
| Hidden API (direct JSON) | `api_scraper.py` | **~2-4 s** |
| Browser automation (Playwright) | `browser_scraper.py` | ~30-60 s |

Faster, lighter, more stable — and it survives frontend redesigns, because the API rarely changes when the page layout does.

## How I found the API (repeatable process)

1. Open `quotes.toscrape.com/js` — a page that renders everything with JavaScript
2. Press **F12** → **Network** tab → filter **Fetch/XHR**
3. Reload the page → a request to **`/api/quotes?page=1`** appears, returning clean JSON
4. Copy the request (URL, headers, pagination parameter) and replicate it with `requests`

That's the entire trick — and it works on a surprising number of real e-commerce, real-estate, and job-listing sites.

## Quick start

```bash
pip install -r requirements.txt
python api_scraper.py                 # fast method → output/quotes.json + quotes.csv

# optional comparison:
pip install playwright && playwright install chromium
python browser_scraper.py             # slow method, same data
```

## Sample output

See [`sample_output/`](sample_output/) for the structured JSON and CSV this produces.

## When I use each approach on client projects

- **Hidden API exists** → direct requests (fast, cheap to run, scales to millions of records)
- **No API / heavy protection** → Playwright with stealth settings, proxies, human-like pacing
- **Official API available** → always preferred; ToS-compliant and stable

## Tech stack

`requests` · Chrome DevTools · `playwright` (comparison) · JSON/CSV output
