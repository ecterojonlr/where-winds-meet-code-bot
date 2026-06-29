from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


THREADS_URL = "https://www.threads.com/@tery0920"


class Threads:

    @staticmethod
    def fetch() -> list[str]:

        posts = []

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            page.goto(
                THREADS_URL,
                wait_until="networkidle",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            html = page.content()

            browser.close()

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
