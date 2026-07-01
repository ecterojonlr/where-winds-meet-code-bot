from dataclasses import dataclass
from pathlib import Path
import json

from playwright.async_api import async_playwright


ARTICLES_FILE = Path("data/bahamut_articles.json")


@dataclass
class BahamutPost:
    id: str
    url: str
    text: str
    source: str


class Bahamut:

    @staticmethod
    async def fetch() -> list[BahamutPost]:
        articles = Bahamut._load_articles()

        if not articles:
            print("沒有設定巴哈姆特文章")
            return []

        posts: list[BahamutPost] = []

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

            for article in articles:
                if not article.get("enabled", True):
                    continue

                url = article.get("url", "").strip()
                name = article.get("name", "巴哈姆特文章")

                if not url:
                    continue

                try:
                    print(f"開始抓取巴哈姆特：{name}")
                    print(url)

                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=60000
                    )

                    await page.wait_for_timeout(5000)

                    article_text = await Bahamut._read_main_article_text(page)

                    if not article_text:
                        print(f"巴哈姆特沒有抓到主文章內容：{name}")
                        continue

                    valid_text = Bahamut._extract_valid_section(
                        text=article_text,
                        start_keywords=article.get("start_keywords", []),
                        stop_keywords=article.get("stop_keywords", [])
                    )

                    if not valid_text:
                        print(f"巴哈姆特沒有找到可用序號區塊：{name}")
                        continue

                    posts.append(
                        BahamutPost(
                            id=Bahamut._make_post_id(
                                url=url,
                                text=valid_text
                            ),
                            url=url,
                            text=valid_text,
                            source=name
                        )
                    )

                    print("=" * 50)
                    print(f"巴哈姆特可用序號區塊：{name}")
                    print(valid_text[:800])

                except Exception as error:
                    print(f"抓取巴哈姆特失敗：{name}")
                    print(error)

            await browser.close()

        print(f"Bahamut 最後回傳 {len(posts)} 篇文章")

        return posts

    @staticmethod
    def _load_articles() -> list[dict]:
        if not ARTICLES_FILE.exists():
            return []

        try:
            with open(ARTICLES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except Exception as error:
            print("讀取 bahamut_articles.json 失敗")
            print(error)
            return []

    @staticmethod
    async def _read_main_article_text(page) -> str:
        """
        只讀主文章，不讀留言區。
        不使用 body，避免把留言、頁尾、介面文字抓進來。
        """

        selectors = [
            ".c-article__content",
            ".FM-P2",
            ".c-post__body",
            ".c-section__main article",
            "article"
        ]

        for selector in selectors:
            try:
                locator = page.locator(selector)
                count = await locator.count()

                if count <= 0:
                    continue

                text = await locator.nth(0).inner_text()

                if text and text.strip():
                    return text.strip()

            except Exception:
                continue

        return ""

    @staticmethod
    def _extract_valid_section(
        text: str,
        start_keywords: list[str],
        stop_keywords: list[str]
    ) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        start_index = -1

        for index, line in enumerate(lines):
            if Bahamut._contains_any(
                text=line,
                keywords=start_keywords
            ):
                start_index = index
                break

        if start_index == -1:
            return ""

        result_lines = []

        for index in range(start_index, len(lines)):
            line = lines[index]

            if index > start_index and Bahamut._contains_any(
                text=line,
                keywords=stop_keywords
            ):
                break

            result_lines.append(line)

        return "\n".join(result_lines)

    @staticmethod
    def _contains_any(
        text: str,
        keywords: list[str]
    ) -> bool:
        if not keywords:
            return False

        upper_text = text.upper()

        for keyword in keywords:
            if keyword.upper() in upper_text:
                return True

        return False

    @staticmethod
    def _make_post_id(
        url: str,
        text: str
    ) -> str:
        base = url + "|" + text[:300]

        return "bahamut-" + str(abs(hash(base)))
