from dataclasses import dataclass
import re

from playwright.async_api import async_playwright


THREADS_URL = "https://www.threads.com/@tery0920"
AUTHOR = "tery0920"


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

            candidates = []

            article_count = await page.locator("article").count()
            print(f"article 數量：{article_count}")

            if article_count > 0:
                article_texts = await page.locator("article").all_inner_texts()
                candidates.extend(article_texts)

            button_texts = await page.locator("div[role='button']").all_inner_texts()
            candidates.extend(button_texts)

            body_text = await page.locator("body").inner_text()
            body_candidates = Threads._split_body_into_posts(body_text)
            candidates.extend(body_candidates)

            await browser.close()

        latest_text = Threads._pick_latest_post(candidates)

        if not latest_text:
            print("沒有找到可用的最新貼文")
            return None

        post_id = Threads._make_post_id(latest_text)

        print("=" * 50)
        print("最新 Threads 貼文：")
        print(latest_text[:1000])
        print("=" * 50)
        print(f"最新貼文 ID：{post_id}")

        return ThreadPost(
            id=post_id,
            url=THREADS_URL,
            text=latest_text
        )

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
    def _pick_latest_post(candidates: list[str]) -> str | None:
        seen = set()

        for raw_text in candidates:
            text = Threads._clean_text(raw_text)

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)

            if Threads._looks_like_real_post(text):
                return text

        return None

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
    def _looks_like_real_post(text: str) -> bool:
        lines = text.splitlines()

        if len(lines) < 3:
            return False

        joined = "\n".join(lines).upper()

        if AUTHOR.upper() not in joined:
            return False

        # 只要裡面有疑似兌換碼，就視為可用貼文
        code_pattern = re.compile(
            r"\b(?=[A-Z0-9]{5,20}\b)(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{5,20}\b"
        )

        codes = code_pattern.findall(joined)

        codes = [
            code for code in codes
            if code != AUTHOR.upper()
        ]

        if codes:
            return True

        # 沒有碼，但有時間格式，也可能是最新貼文
        time_keywords = [
            "分鐘",
            "小時",
            "天",
            "週",
            "月",
            "m",
            "h",
            "d",
        ]

        for keyword in time_keywords:
            if keyword in text:
                return True

        return False

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
