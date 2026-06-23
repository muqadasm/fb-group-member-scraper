from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from dateutil import parser


MONTH_YEAR_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
    re.IGNORECASE,
)
FULL_DATE_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
    re.IGNORECASE,
)
RELATIVE_RE = re.compile(r"\b(\d+)\s+(day|week|month|year)s?\s+ago\b", re.IGNORECASE)


def parse_joined_date(text: str, today: date | None = None) -> date | None:
    if not text:
        return None

    today = today or date.today()
    normalized = " ".join(text.split())

    relative = RELATIVE_RE.search(normalized)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2).lower()
        if unit == "day":
            return today - timedelta(days=amount)
        if unit == "week":
            return today - timedelta(weeks=amount)
        if unit == "month":
            return today - timedelta(days=amount * 30)
        if unit == "year":
            return today - timedelta(days=amount * 365)

    full_match = FULL_DATE_RE.search(normalized)
    if full_match:
        return parser.parse(full_match.group(0), fuzzy=True).date()

    month_year_match = MONTH_YEAR_RE.search(normalized)
    if month_year_match:
        parsed = parser.parse(month_year_match.group(0), fuzzy=True, default=datetime(1900, 1, 1))
        return parsed.date()

    try:
        return parser.parse(normalized, fuzzy=True).date()
    except (ValueError, OverflowError):
        return None


def is_on_or_after(joined_text: str, cutoff: date | None) -> bool:
    if cutoff is None:
        return True

    joined = parse_joined_date(joined_text)
    if joined is None:
        return False

    return joined >= cutoff
