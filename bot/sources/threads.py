from dataclasses import dataclass
import re

from playwright.async_api import async_playwright


THREADS_URL = "https://www.threads.com/@tery0920"
AUTHOR = "tery0920"
MAX_POSTS = 5


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
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            page = await browser.new_page(
                viewport={"width": 1280, "height": 1800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            )

            await page.goto(
                THREADS_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(10000)

            for _ in range(3):
                await page.mouse.wheel(0, 2500)
                await page.wait_for_timeout(2000)

            texts = []

            article_count = await page.locator("article").count()
            print(f"article 數量：{article_count}")

            if article_count > 0:
                article_texts = await page.locator("article").all_inner_texts()
                texts.extend(article_texts)

            if not texts:
                print("article 抓不到，改抓 body 文字")
                body_text = await page.locator("body").inner_text()
                texts = Threads._split_body_into_posts(body_text)

            await browser.close()

        seen = set()

        for text in texts:
            clean_text = Threads._clean_text(text)

            if not clean_text:
                continue

            if clean_text in seen:
                continue

            seen.add(clean_text)

            if not Threads._looks_like_post(clean_text):
                continue

            post_id = Threads._make_post_id(clean_text)

            posts.append(
                ThreadPost(
                    id=post_id,
                    url=THREADS_URL,
                    text=clean_text
                )
            )

            if len(posts) >= MAX_POSTS:
                break

        print(f"Threads 最後回傳 {len(posts)} 篇貼文")

        for index, post in enumerate(posts):
            print("=" * 50)
            print(f"第 {index + 1} 篇貼文")
            print(post.text[:800])

        return posts

    @staticmethod
    def _split_body_into_posts(text: str) -> list[str]:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        posts = []
        current = []
        started = False

        for line in lines:
            if line.lower() == AUTHOR:
                if started and current:
                    posts.append("\n".join(current))
                    current = []

                started = True
                current.append(line)
                continue

            if started:
                current.append(line)

        if current:
            posts.append("\n".join(current))

        return posts

    @staticmethod
    def _clean_text(text: str) -> str:
        ignore_lines = {
            "Like",
            "Reply",
            "Repost",
            "Share",
            "讚",
            "回覆",
            "轉發",
            "分享",
            "Log in",
            "Sign up",
            "登入",
            "註冊",
            "Threads",
            "Instagram",
        }

        lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line in ignore_lines:
                continue

            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def _looks_like_post(text: str) -> bool:
        if AUTHOR.upper() not in text.upper():
            return False

        if len(text) < 20:
            return False

        return True

    @staticmethod
    def _make_post_id(text: str) -> str:
        useful_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.lower() == AUTHOR:
                continue

            useful_lines.append(line)

        base = "|".join(useful_lines[:6])

        return str(abs(hash(base)))
