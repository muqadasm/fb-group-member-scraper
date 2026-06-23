from datetime import date

from fb_group_member_scraper.date_parser import is_on_or_after, parse_joined_date


def test_parse_full_date() -> None:
    assert parse_joined_date("Joined January 15, 2024") == date(2024, 1, 15)


def test_parse_month_year() -> None:
    assert parse_joined_date("Member since March 2023") == date(2023, 3, 1)


def test_parse_relative_days() -> None:
    assert parse_joined_date("Joined 3 days ago", today=date(2026, 6, 23)) == date(2026, 6, 20)


def test_filter_cutoff() -> None:
    assert is_on_or_after("Joined January 15, 2024", date(2024, 1, 1))
    assert not is_on_or_after("Joined January 15, 2023", date(2024, 1, 1))
