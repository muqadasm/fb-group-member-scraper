from __future__ import annotations

from datetime import datetime

from .models import MemberRecord, ScrapeRunSummary


def build_summary(
    records: list[MemberRecord],
    source_count: int,
    output_files: list[str],
    started_at: datetime,
    finished_at: datetime,
) -> ScrapeRunSummary:
    unique_profiles = {record.profile_url for record in records if record.profile_url}
    return ScrapeRunSummary(
        source_count=source_count,
        record_count=len(records),
        unique_profile_count=len(unique_profiles),
        output_files=output_files,
        started_at=started_at,
        finished_at=finished_at,
    )
