from __future__ import annotations

import asyncio
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urljoin

from playwright.async_api import BrowserContext, Page, async_playwright

from .date_parser import parse_joined_date
from .models import MemberRecord


class FacebookGroupMemberScraper:
    def __init__(
        self,
        user_data_dir: Path,
        headed: bool = True,
        slow_mo_ms: int = 80,
        scroll_pause_seconds: float = 1.8,
    ) -> None:
        self.user_data_dir = user_data_dir
        self.headed = headed
        self.slow_mo_ms = slow_mo_ms
        self.scroll_pause_seconds = scroll_pause_seconds

    async def scrape_group(
        self,
        group_url: str,
        max_scrolls: int,
        joined_after: date | None = None,
    ) -> list[MemberRecord]:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=not self.headed,
                slow_mo=self.slow_mo_ms,
                viewport={"width": 1366, "height": 900},
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(group_url, wait_until="domcontentloaded", timeout=90_000)
                await self.wait_for_user_login(page)
                await self.scroll_members_page(page, max_scrolls=max_scrolls)
                return await self.collect_member_cards(page, group_url, joined_after)
            finally:
                await context.close()

    async def wait_for_user_login(self, page: Page) -> None:
        login_selectors = [
            "input[name='email']",
            "input[name='pass']",
            "text=Log in",
        ]
        login_detected = False
        for selector in login_selectors:
            if await page.locator(selector).count():
                login_detected = True
                break

        if login_detected:
            print("Facebook login detected. Please log in in the opened browser window.")
            print("After the group members page loads, press Enter here to continue.")
            await asyncio.to_thread(input)

    async def scroll_members_page(self, page: Page, max_scrolls: int) -> None:
        last_height = 0
        stable_rounds = 0

        for _ in range(max_scrolls):
            await page.mouse.wheel(0, 1800)
            await page.wait_for_timeout(int(self.scroll_pause_seconds * 1000))
            current_height = await page.evaluate("document.body.scrollHeight")

            if current_height == last_height:
                stable_rounds += 1
                if stable_rounds >= 3:
                    break
            else:
                stable_rounds = 0
                last_height = current_height

    async def collect_member_cards(
        self,
        page: Page,
        group_url: str,
        joined_after: date | None,
    ) -> list[MemberRecord]:
        records: list[MemberRecord] = []
        seen_profile_urls: set[str] = set()

        card_locators = page.locator("div[role='article'], div[data-visualcompletion='ignore-dynamic']")
        count = await card_locators.count()

        for index in range(count):
            card = card_locators.nth(index)
            text = clean_text(await safe_inner_text(card))
            if not text:
                continue

            profile_url = await self.extract_profile_url(card)
            name = await self.extract_name(card, text)
            if not name or not profile_url or profile_url in seen_profile_urls:
                continue

            joined_text = extract_joined_text(text)
            joined_date = parse_joined_date(joined_text)
            if joined_after and (joined_date is None or joined_date < joined_after):
                continue

            records.append(
                MemberRecord(
                    group_url=group_url,
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

    async def extract_profile_url(self, card) -> str:
        links = card.locator("a[href*='facebook.com'], a[href^='/']")
        link_count = await links.count()

        for index in range(link_count):
            href = await links.nth(index).get_attribute("href")
            if not href:
                continue
            if any(skip in href for skip in ["/groups/", "/posts/", "/photos/", "/events/"]):
                continue
            return normalize_facebook_url(href)

        return ""

    async def extract_name(self, card, fallback_text: str) -> str:
        links = card.locator("a[role='link'], strong a, span a")
        link_count = await links.count()

        for index in range(link_count):
            label = clean_text(await safe_inner_text(links.nth(index)))
            if label and len(label) <= 80 and not looks_like_action(label):
                return label

        first_line = fallback_text.splitlines()[0].strip()
        return first_line if first_line and not looks_like_action(first_line) else ""


async def safe_inner_text(locator) -> str:
    try:
        return await locator.inner_text(timeout=1000)
    except Exception:
        return ""


def clean_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def normalize_facebook_url(href: str) -> str:
    absolute = urljoin("https://www.facebook.com", href)
    return absolute.split("?")[0]


def extract_joined_text(text: str) -> str:
    for line in text.splitlines():
        lower = line.lower()
        if "joined" in lower or "member since" in lower:
            return line.strip()
    return ""


def extract_role_text(text: str) -> str:
    role_keywords = ["admin", "moderator", "group expert", "new member"]
    for line in text.splitlines():
        lower = line.lower()
        if any(keyword in lower for keyword in role_keywords):
            return line.strip()
    return ""


def looks_like_action(text: str) -> bool:
    return text.lower() in {
        "add friend",
        "message",
        "invite",
        "join",
        "joined",
        "more",
        "see more",
    }
