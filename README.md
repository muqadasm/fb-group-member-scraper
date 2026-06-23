# Facebook Group Member Scraper

Portfolio-style Python scraper inspired by a Facebook group member extraction workflow.

This project uses Playwright to open a real browser session, scroll a Facebook group members page, collect member cards that are visible to the logged-in user, optionally filter by join date, and export results to CSV.

## Important Use

Use this only for groups you own, administer, or have permission to analyze. The scraper does not bypass login, private groups, paywalls, CAPTCHAs, rate limits, or hidden member data.

## Features

- Opens a persistent browser profile so you can log in normally
- Collects visible member name, profile URL, role/status text, and detected join date text
- Optional date filtering with `--joined-after`
- Human-paced scrolling with configurable limits
- Exports clean CSV files
- Includes tests for date parsing and filtering logic

## Project Structure

```text
fb_group_member_scraper/
  src/fb_group_member_scraper/
    cli.py
    date_parser.py
    facebook_scraper.py
    models.py
    writer.py
  data/
    group_urls.txt
  exports/
  tests/
    test_date_parser.py
  requirements.txt
  README.md
```

## Install

```bash
cd fb_group_member_scraper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python -m playwright install chromium
```

## Add Group URLs

Edit:

```text
data/group_urls.txt
```

Put one Facebook group members URL per line:

```text
https://www.facebook.com/groups/YOUR_GROUP_ID/members
```

## Run

First run opens Chromium. Log in manually if Facebook asks.

```bash
fb-group-members --input data/group_urls.txt --output exports/members.csv --max-scrolls 30 --headed
```

Filter members joined after a date:

```bash
fb-group-members --input data/group_urls.txt --output exports/recent_members.csv --joined-after 2024-01-01 --max-scrolls 50 --headed
```

Run in visible mode, recommended:

```bash
fb-group-members --input data/group_urls.txt --output exports/members.csv --headed
```

## Output Columns

- `group_url`
- `name`
- `profile_url`
- `role_text`
- `joined_text`
- `joined_date`
- `scraped_at`

## Tests

```bash
pytest
```

## Notes

Facebook changes its page HTML often. If selectors stop working, update `facebook_scraper.py`, especially the `collect_member_cards` method.
