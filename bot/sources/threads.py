from dataclasses import dataclass

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
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = await browser.new_page(
                viewport={
                    "width": 1280,
                    "height": 1600
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            await page.goto(
                THREADS_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(8000)

            # 往下滑幾次，讓 Threads 載入更多貼文
            for _ in range(3):
                await page.mouse.wheel(0, 2500)
                await page.wait_for_timeout(2000)

            # 直接從畫面抓文字，不再依賴 BeautifulSoup / article
            raw_blocks = await page.locator("div[role='button']").all_inner_texts()

            seen_ids = set()

            for index, block in enumerate(raw_blocks):

                text = Threads._clean_text(block)

                if not Threads._looks_like_post(text):
                    continue

                post_id = f"threads-post-{index}"

                if post_id in seen_ids:
                    continue

                seen_ids.add(post_id)

                posts.append(
                    ThreadPost(
                        id=post_id,
                        url=THREADS_URL,
                        text=text
                    )
                )

                if len(posts) >= MAX_POSTS:
                    break

            await browser.close()

        print(f"Threads 抓到 {len(posts)} 篇可能貼文")

        return posts

    @staticmethod
    def _clean_text(text: str) -> str:

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if line in {
                "Like",
                "Reply",
                "Repost",
                "Share",
                "讚",
                "回覆",
                "轉發",
                "分享"
            }:
                continue

            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def _looks_like_post(text: str) -> bool:

        if not text:
            return False

        if len(text) < 10:
            return False

        blocked_keywords = [
            "Log in",
            "Sign up",
            "登入",
            "註冊",
            "Threads",
            "Instagram"
        ]

        for keyword in blocked_keywords:
            if text.strip() == keyword:
                return False

        return True
