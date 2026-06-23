from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path

from .facebook_scraper import FacebookGroupMemberScraper
from .writer import write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape visible Facebook group member cards.")
    parser.add_argument("--input", required=True, type=Path, help="Text file containing group member URLs.")
    parser.add_argument("--output", required=True, type=Path, help="CSV output path.")
    parser.add_argument("--demo", action="store_true", help="Run against the included local demo members page.")
    parser.add_argument("--large-demo", action="store_true", help="Run against the included large local demo members page.")
    parser.add_argument("--joined-after", type=str, default=None, help="Only keep members joined on/after YYYY-MM-DD.")
    parser.add_argument("--max-scrolls", type=int, default=30, help="Maximum scroll rounds per group.")
    parser.add_argument("--profile-dir", type=Path, default=Path(".browser-profile"), help="Persistent browser profile directory.")
    parser.add_argument("--headed", action="store_true", help="Show the browser window.")
    return parser.parse_args()


def read_group_urls(path: Path) -> list[str]:
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            urls.append(stripped)
    return urls


async def main_async() -> None:
    args = parse_args()
    joined_after = datetime.strptime(args.joined_after, "%Y-%m-%d").date() if args.joined_after else None
    if args.large_demo:
        demo_page = Path(__file__).resolve().parents[2] / "data" / "large_demo_members.html"
        group_urls = [demo_page.as_uri()]
    elif args.demo:
        demo_page = Path(__file__).resolve().parents[2] / "data" / "demo_members.html"
        group_urls = [demo_page.as_uri()]
    else:
        group_urls = read_group_urls(args.input)

    if not group_urls:
        raise SystemExit(f"No group URLs found in {args.input}")

    scraper = FacebookGroupMemberScraper(
        user_data_dir=args.profile_dir,
        headed=args.headed,
    )

    all_records = []
    for group_url in group_urls:
        print(f"Scraping: {group_url}")
        records = await scraper.scrape_group(
            group_url=group_url,
            max_scrolls=args.max_scrolls,
            joined_after=joined_after,
        )
        print(f"Collected {len(records)} records from this group.")
        all_records.extend(records)

    written = write_csv(all_records, args.output)
    print(f"Done. Wrote {written} records to {args.output}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
