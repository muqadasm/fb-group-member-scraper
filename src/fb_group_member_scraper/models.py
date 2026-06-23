from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class MemberRecord:
    group_url: str
    name: str
    profile_url: str
    role_text: str
    joined_text: str
    joined_date: str
    scraped_at: datetime


@dataclass(slots=True)
class ScrapeRunSummary:
    source_count: int
    record_count: int
    unique_profile_count: int
    output_files: list[str]
    started_at: datetime
    finished_at: datetime

    @property
    def duration_seconds(self) -> float:
        return round((self.finished_at - self.started_at).total_seconds(), 2)
