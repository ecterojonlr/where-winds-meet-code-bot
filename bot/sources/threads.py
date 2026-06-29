from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


THREADS_URL = "https://www.threads.com/@tery0920"


class Threads:

    @staticmethod
    async def fetch() -> list[str]:

        posts = []

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            await page.goto(
                THREADS_URL,
                wait_until="networkidle",
                timeout=60000
            )

            # 等待 Threads 載入內容
            await page.wait_for_timeout(5000)

            html = await page.content()

            await browser.close()

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        article_list = soup.find_all("article")

        for article in article_list:

            text = article.get_text(
                separator="\n",
                strip=True
            )

            if text:
                posts.append(text)

        return posts
