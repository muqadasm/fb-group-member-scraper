from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .models import MemberRecord


FIELDNAMES = [
    "group_url",
    "name",
    "profile_url",
    "role_text",
    "joined_text",
    "joined_date",
    "scraped_at",
]


def write_csv(records: Iterable[MemberRecord], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for record in records:
            writer.writerow(
                {
                    "group_url": record.group_url,
                    "name": record.name,
                    "profile_url": record.profile_url,
                    "role_text": record.role_text,
                    "joined_text": record.joined_text,
                    "joined_date": record.joined_date,
                    "scraped_at": record.scraped_at.isoformat(timespec="seconds"),
                }
            )
            count += 1

    return count
