# Facebook Group Member Scraper

Professional Python scraping project built with Playwright. It opens a real browser session, collects visible Facebook group member cards that the logged-in user is allowed to view, filters by join date, and exports clean CSV/JSON datasets with a run summary.

> Use this only for groups you own, administer, or have permission to analyze. This project does not bypass login, private groups, CAPTCHAs, rate limits, or hidden member data.

## Highlights

- Browser automation with Playwright
- Persistent browser profile for normal manual login
- CSV and JSON export modes
- Optional `--joined-after` date filter
- Duplicate input URL cleanup
- Navigation timeout and retry controls
- Structured run summary JSON
- Local demo pages, including a large demo dataset
- Unit tests and GitHub Actions CI

## Project Structure

```text
fb_group_member_scraper/
  .github/workflows/tests.yml
  data/
    demo_members.html
    large_demo_members.html
    group_urls.txt
  src/fb_group_member_scraper/
    cli.py
    date_parser.py
    facebook_scraper.py
    models.py
    reporting.py
    writer.py
  tests/
  pyproject.toml
  requirements.txt
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m playwright install chromium
```

## Run Large Demo

No Facebook URL required:

```powershell
$env:PYTHONPATH="$PWD\src"
python -m fb_group_member_scraper.cli --input data/group_urls.txt --output exports/large_demo_members.csv --max-scrolls 5 --headed --large-demo --format both --summary-output exports/run_summary.json
```

This creates:

```text
exports/large_demo_members.csv
exports/large_demo_members.json
exports/run_summary.json
```

## Run With Your Own Group

Edit:

```text
data/group_urls.txt
```

Add one members page URL per line:

```text
https://www.facebook.com/groups/YOUR_GROUP_ID/members
```

Then run:

```powershell
$env:PYTHONPATH="$PWD\src"
python -m fb_group_member_scraper.cli --input data/group_urls.txt --output exports/members.csv --max-scrolls 30 --headed --format both --summary-output exports/run_summary.json
```

Filter recent members:

```powershell
$env:PYTHONPATH="$PWD\src"
python -m fb_group_member_scraper.cli --input data/group_urls.txt --output exports/recent_members.csv --joined-after 2024-01-01 --max-scrolls 50 --headed
```

## CLI Options

```text
--input            Text file containing group member URLs
--output           CSV output path
--format           csv, json, or both
--summary-output   Optional JSON run summary path
--joined-after     Keep only members joined on/after YYYY-MM-DD
--max-scrolls      Maximum scroll rounds per group
--profile-dir      Persistent browser profile directory
--retries          Navigation retry count
--timeout-ms       Navigation timeout in milliseconds
--headed           Show browser window
--demo             Run small local demo
--large-demo       Run large local demo
--log-level        DEBUG, INFO, WARNING, or ERROR
```

## Output Columns

- `group_url`
- `name`
- `profile_url`
- `role_text`
- `joined_text`
- `joined_date`
- `scraped_at`

## Test

```powershell
$env:PYTHONPATH="$PWD\src"
pytest
```

## GitHub Push

```powershell
git add .
git commit -m "Upgrade scraper project with exports, summary, retries, and CI"
git push -u origin main
```

## Notes

Facebook changes page markup often. If collection stops working on real pages, update selectors in `src/fb_group_member_scraper/facebook_scraper.py`.
