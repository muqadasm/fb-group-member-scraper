from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import MemberRecord, ScrapeRunSummary


FIELDNAMES = [
    "group_url",
    "name",
    "profile_url",
    "role_text",
    "joined_text",
    "joined_date",
    "scraped_at",
]


def record_to_dict(record: MemberRecord) -> dict[str, str]:
    return {
        "group_url": record.group_url,
        "name": record.name,
        "profile_url": record.profile_url,
        "role_text": record.role_text,
        "joined_text": record.joined_text,
        "joined_date": record.joined_date,
        "scraped_at": record.scraped_at.isoformat(timespec="seconds"),
    }


def write_csv(records: Iterable[MemberRecord], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for record in records:
            writer.writerow(record_to_dict(record))
            count += 1

    return count


def write_json(records: Iterable[MemberRecord], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [record_to_dict(record) for record in records]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return len(payload)


def write_summary(summary: ScrapeRunSummary, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_count": summary.source_count,
        "record_count": summary.record_count,
        "unique_profile_count": summary.unique_profile_count,
        "output_files": summary.output_files,
        "started_at": summary.started_at.isoformat(timespec="seconds"),
        "finished_at": summary.finished_at.isoformat(timespec="seconds"),
        "duration_seconds": summary.duration_seconds,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
