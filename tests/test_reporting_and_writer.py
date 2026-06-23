import json
from datetime import datetime

from fb_group_member_scraper.models import MemberRecord
from fb_group_member_scraper.reporting import build_summary
from fb_group_member_scraper.writer import write_json


def sample_record(name: str, profile_url: str) -> MemberRecord:
    return MemberRecord(
        group_url="file:///demo.html",
        name=name,
        profile_url=profile_url,
        role_text="Member",
        joined_text="Joined January 1, 2024",
        joined_date="2024-01-01",
        scraped_at=datetime(2026, 6, 23, 12, 0, 0),
    )


def test_build_summary_counts_unique_profiles() -> None:
    records = [
        sample_record("A", "https://facebook.com/a"),
        sample_record("A duplicate", "https://facebook.com/a"),
        sample_record("B", "https://facebook.com/b"),
    ]

    summary = build_summary(
        records=records,
        source_count=1,
        output_files=["exports/members.csv"],
        started_at=datetime(2026, 6, 23, 12, 0, 0),
        finished_at=datetime(2026, 6, 23, 12, 0, 5),
    )

    assert summary.record_count == 3
    assert summary.unique_profile_count == 2
    assert summary.duration_seconds == 5


def test_write_json_exports_records(tmp_path) -> None:
    output = tmp_path / "members.json"
    written = write_json([sample_record("A", "https://facebook.com/a")], output)

    assert written == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload[0]["name"] == "A"
    assert payload[0]["joined_date"] == "2024-01-01"
