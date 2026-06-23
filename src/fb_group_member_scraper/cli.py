from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from .facebook_scraper import FacebookGroupMemberScraper
from .reporting import build_summary
from .static_scraper import scrape_static_members_page
from .writer import write_csv, write_json, write_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape visible Facebook group member cards.")
    parser.add_argument("--input", required=True, type=Path, help="Text file containing group member URLs.")
    parser.add_argument("--output", required=True, type=Path, help="CSV output path.")
    parser.add_argument("--demo", action="store_true", help="Run against the included local demo members page.")
    parser.add_argument("--large-demo", action="store_true", help="Run against the included large local demo members page.")
    parser.add_argument("--joined-after", type=str, default=None, help="Only keep members joined on/after YYYY-MM-DD.")
    parser.add_argument("--max-scrolls", type=int, default=30, help="Maximum scroll rounds per group.")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="csv", help="Export format.")
    parser.add_argument("--summary-output", type=Path, default=None, help="Optional JSON run summary path.")
    parser.add_argument("--profile-dir", type=Path, default=Path(".browser-profile"), help="Persistent browser profile directory.")
    parser.add_argument("--retries", type=int, default=2, help="Navigation retry count per URL.")
    parser.add_argument("--timeout-ms", type=int, default=90_000, help="Page navigation timeout in milliseconds.")
    parser.add_argument("--headed", action="store_true", help="Show the browser window.")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    return parser.parse_args()


def read_group_urls(path: Path) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped not in seen:
            urls.append(stripped)
            seen.add(stripped)
    return urls


async def main_async() -> None:
    args = parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s %(message)s")
    started_at = datetime.now().astimezone()
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
        navigation_timeout_ms=args.timeout_ms,
        retries=args.retries,
    )

    all_records = []
    for group_url in group_urls:
        print(f"Scraping: {group_url}")
        if group_url.startswith("file://"):
            records = scrape_static_members_page(group_url, joined_after=joined_after)
        else:
            records = await scraper.scrape_group(
                group_url=group_url,
                max_scrolls=args.max_scrolls,
                joined_after=joined_after,
            )
        print(f"Collected {len(records)} records from this group.")
        all_records.extend(records)

    output_files: list[str] = []
    if args.format in {"csv", "both"}:
        written = write_csv(all_records, args.output)
        output_files.append(str(args.output))
        print(f"Wrote {written} CSV records to {args.output}")

    if args.format in {"json", "both"}:
        json_output = args.output.with_suffix(".json") if args.output.suffix else args.output
        written = write_json(all_records, json_output)
        output_files.append(str(json_output))
        print(f"Wrote {written} JSON records to {json_output}")

    finished_at = datetime.now().astimezone()
    summary = build_summary(
        records=all_records,
        source_count=len(group_urls),
        output_files=output_files,
        started_at=started_at,
        finished_at=finished_at,
    )
    if args.summary_output:
        write_summary(summary, args.summary_output)
        print(f"Wrote run summary to {args.summary_output}")

    print(
        "Done. "
        f"Sources: {summary.source_count}; "
        f"records: {summary.record_count}; "
        f"unique profiles: {summary.unique_profile_count}; "
        f"duration: {summary.duration_seconds}s"
    )


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
