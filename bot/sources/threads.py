from dataclasses import dataclass

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


THREADS_URL = "https://www.threads.com/@tery0920"
MAX_POSTS = 20


@dataclass
class ThreadPost:
    id: str
    url: str
    text: str


class Threads:
    @staticmethod
    async def fetch() -> list[ThreadPost]:
        posts: list[ThreadPost] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            await page.goto(
                THREADS_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(8000)

            html = await page.content()

            await browser.close()

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        articles = soup.find_all("article")

        for index, article in enumerate(articles[:MAX_POSTS]):
            text = article.get_text(
                separator="\n",
                strip=True
            )

            if not text:
                continue

            url = THREADS_URL
            post_id = f"threads-post-{index}"

            link = article.find("a", href=True)

            if link:
                href = link["href"]

                if href.startswith("/"):
                    url = "https://www.threads.com" + href
                elif href.startswith("http"):
                    url = href

                post_id = url.rstrip("/").split("/")[-1]

            posts.append(
                ThreadPost(
                    id=post_id,
                    url=url,
                    text=text
                )
            )

        return posts
