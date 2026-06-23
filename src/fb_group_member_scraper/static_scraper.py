from __future__ import annotations

from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from .date_parser import parse_joined_date
from .facebook_scraper import extract_joined_text, extract_role_text, normalize_facebook_url
from .models import MemberRecord


class MemberCardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict[str, str | list[str]]] = []
        self.current_card: dict[str, str | list[str]] | None = None
        self.current_link_href = ""
        self.capture_text = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        if tag == "div" and attrs_dict.get("role") == "article":
            self.current_card = {"name": "", "profile_url": "", "lines": []}
            return

        if self.current_card is None:
            return

        if tag == "a":
            self.current_link_href = attrs_dict.get("href", "")
            self.capture_text = True
        elif tag in {"p", "span", "strong"}:
            self.capture_text = True

    def handle_data(self, data: str) -> None:
        if self.current_card is None or not self.capture_text:
            return

        text = " ".join(data.split())
        if not text:
            return

        lines = self.current_card["lines"]
        assert isinstance(lines, list)
        lines.append(text)

        if self.current_link_href and not self.current_card["name"]:
            self.current_card["name"] = text
            self.current_card["profile_url"] = normalize_facebook_url(self.current_link_href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.current_link_href = ""
            self.capture_text = False
        elif tag in {"p", "span", "strong"}:
            self.capture_text = False
        elif tag == "div" and self.current_card is not None:
            self.cards.append(self.current_card)
            self.current_card = None
            self.capture_text = False


def scrape_static_members_page(
    page_url: str,
    joined_after: date | None = None,
) -> list[MemberRecord]:
    path = path_from_file_url(page_url)
    parser = MemberCardParser()
    parser.feed(path.read_text(encoding="utf-8"))

    records: list[MemberRecord] = []
    seen_profile_urls: set[str] = set()
    for card in parser.cards:
        name = str(card.get("name") or "")
        profile_url = str(card.get("profile_url") or "")
        lines = card.get("lines") or []
        text = "\n".join(str(line) for line in lines)
        joined_text = extract_joined_text(text)
        joined_date = parse_joined_date(joined_text)

        if not name or not profile_url or profile_url in seen_profile_urls:
            continue
        if joined_after and (joined_date is None or joined_date < joined_after):
            continue

        records.append(
            MemberRecord(
                group_url=page_url,
                name=name,
                profile_url=profile_url,
                role_text=extract_role_text(text),
                joined_text=joined_text,
                joined_date=joined_date.isoformat() if joined_date else "",
                scraped_at=datetime.now().astimezone(),
            )
        )
        seen_profile_urls.add(profile_url)

    return records


def path_from_file_url(page_url: str) -> Path:
    parsed = urlparse(page_url)
    if parsed.scheme != "file":
        raise ValueError(f"Static scraper only supports file URLs, got: {page_url}")
    return Path(unquote(parsed.path.lstrip("/")))
