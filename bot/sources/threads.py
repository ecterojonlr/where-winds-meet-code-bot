from dataclasses import dataclass

from playwright.async_api import async_playwright


THREADS_URL = "https://www.threads.com/@tery0920"


@dataclass
class ThreadPost:
    id: str
    url: str
    text: str


class Threads:

    @staticmethod
    async def fetch_latest() -> ThreadPost | None:

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

            text = None

            article_count = await page.locator("article").count()
            print(f"article 數量：{article_count}")

            if article_count > 0:
                # 只抓第一篇 article，也就是最新一篇
                text = await page.locator("article").nth(0).inner_text()
            else:
                print("article 抓不到，改用 body fallback")

                body_text = await page.locator("body").inner_text()
                text = Threads._extract_first_post_from_body(body_text)

            await browser.close()

        if not text:
            print("沒有抓到最新貼文文字")
            return None

        clean_text = Threads._clean_text(text)

        if not clean_text:
            print("最新貼文清理後為空")
            return None

        post_id = Threads._make_post_id(clean_text)

        print("=" * 50)
        print("最新 Threads 貼文：")
        print(clean_text[:1000])
        print("=" * 50)
        print(f"最新貼文 ID：{post_id}")

        return ThreadPost(
            id=post_id,
            url=THREADS_URL,
            text=clean_text
        )

    @staticmethod
    def _extract_first_post_from_body(text: str) -> str:
        lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            lines.append(line)

        if not lines:
            return ""

        result = []

        started = False

        for line in lines:
            # 找到作者帳號後，開始收最新一篇
            if line.lower() == "tery0920":
                if started:
                    break

                started = True
                result.append(line)
                continue

            if started:
                # 遇到第二篇或其他推薦內容就停止
                if line.lower() in {
                    "reply",
                    "repost",
                    "share",
                    "like",
                    "回覆",
                    "轉發",
                    "分享",
                    "讚",
                }:
                    continue

                result.append(line)

                # 粗略限制，避免整頁都被收進來
                if len(result) >= 12:
                    break

        return "\n".join(result)

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

    @staticmethod
    def _make_post_id(text: str) -> str:
        lines = text.splitlines()

        useful_lines = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.lower() == "tery0920":
                continue

            useful_lines.append(line)

        base = "|".join(useful_lines[:5])

        return str(abs(hash(base)))
