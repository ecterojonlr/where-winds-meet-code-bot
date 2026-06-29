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
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            page = await browser.new_page(
                viewport={
                    "width": 1280,
                    "height": 1800
                },
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

            for _ in range(5):
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
                texts.append(body_text)

            await browser.close()

        seen = set()

        for index, text in enumerate(texts):
            clean_text = Threads._clean_text(text)

            if not clean_text:
                continue

            if clean_text in seen:
                continue

            seen.add(clean_text)

            print("=" * 50)
            print(f"Threads 文字區塊 {index + 1}")
            print(clean_text[:1500])

            posts.append(
                ThreadPost(
                    id=f"threads-post-{index}",
                    url=THREADS_URL,
                    text=clean_text
                )
            )

            if len(posts) >= MAX_POSTS:
                break

        print(f"Threads 最後回傳 {len(posts)} 篇文字")

        return posts

    @staticmethod
    def _clean_text(text: str) -> str:
        lines = []

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
        }

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line in ignore_lines:
                continue

            lines.append(line)

        return "\n".join(lines)
