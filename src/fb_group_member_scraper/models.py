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

