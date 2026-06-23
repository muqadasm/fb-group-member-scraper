from pathlib import Path

from fb_group_member_scraper.static_scraper import scrape_static_members_page


def test_scrape_static_members_page() -> None:
    demo_page = Path("data/demo_members.html").resolve().as_uri()
    records = scrape_static_members_page(demo_page)

    assert len(records) == 3
    assert records[0].name == "John Demo"
    assert records[0].joined_date == "2024-01-15"
