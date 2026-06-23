from pathlib import Path

from fb_group_member_scraper.static_scraper import path_from_file_url, scrape_static_members_page


def test_scrape_static_members_page() -> None:
    demo_page = Path("data/demo_members.html").resolve().as_uri()
    records = scrape_static_members_page(demo_page)

    assert len(records) == 3
    assert records[0].name == "John Demo"
    assert records[0].joined_date == "2024-01-15"


def test_path_from_file_url_round_trips_current_platform() -> None:
    path = Path("data/demo_members.html").resolve()

    assert path_from_file_url(path.as_uri()) == path
