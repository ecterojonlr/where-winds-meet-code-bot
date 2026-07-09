from dataclasses import dataclass
import asyncio
import re

from playwright.async_api import async_playwright


CODES_YAR_URL = "https://codes.yar.gg/"


@dataclass
class CodesYarPost:
    id: str
    url: str
    text: str
    source: str


class CodesYar:

    CODE_PATTERN = re.compile(
        r"\b[A-Z0-9]{5,20}\b"
    )

    BLOCKLIST = {
        "ENGLISH",
        "ESPANOL",
        "FRANCAIS",
        "DEUTSCH",
        "ITALIANO",
        "PORTUGUES",
        "RUSSIAN",
        "TURKCE",
        "ARABIC",
        "CHINESE",
        "JAPANESE",
        "KOREAN",
        "THAI",
        "VIETNAMESE",
        "INDONESIA",
        "MALAYSIA",
        "PIRATE",

        "SUBMIT",
        "CONTACT",
        "CANCEL",
        "CONFIRM",
        "REPORT",
        "ARCHIVED",
        "ACTIVE",
        "UNUSED",
        "USED",
        "EXPIRED",
        "CODES",
        "CODE",
        "COUPON",
        "COPY",
        "COPIED",
        "PREVIOUS",
        "NEXT",
        "BACK",
        "SKIP",
        "LEFT",
        "FILTER",
        "REFERENCE",
        "DEVICE",
        "VALID",
        "INVALID",
        "REDEEM",
        "REDEEMED",
        "RATE",
        "LIMITED",

        "WHERE",
        "WINDS",
        "MEET",
        "WWM",
        "YARGG",
    }

    @staticmethod
    async def fetch() -> list[CodesYarPost]:
        collected_texts: list[str] = []
        response_tasks = []

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

            page.on(
                "response",
                lambda response: response_tasks.append(
                    asyncio.create_task(
                        CodesYar._capture_response(
                            response=response,
                            collected_texts=collected_texts
                        )
                    )
                )
            )

            try:
                print("開始抓取 codes.yar.gg 的 All 分頁")
                print(CODES_YAR_URL)

                await page.goto(
                    CODES_YAR_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(5000)

                # 嘗試切換到 All 分頁
                # 如果 All 本來就是預設頁，點不到也不影響
                try:
                    await page.get_by_role(
                        "button",
                        name="All",
                        exact=True
                    ).click(timeout=3000)

                    await page.wait_for_timeout(2000)

                except Exception:
                    try:
                        await page.get_by_text(
                            "All",
                            exact=True
                        ).click(timeout=3000)

                        await page.wait_for_timeout(2000)

                    except Exception:
                        print("codes.yar.gg 找不到 All 按鈕，使用目前頁面內容")

                # 只抓目前 All 頁面內容
                body_text = await CodesYar._safe_body_text(page)

                if body_text:
                    collected_texts.append(body_text)

                # 抓 localStorage / sessionStorage
                storage_text = await page.evaluate(
                    """
                    () => {
                        const data = [];

                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            data.push(key + "=" + localStorage.getItem(key));
                        }

                        for (let i = 0; i < sessionStorage.length; i++) {
                            const key = sessionStorage.key(i);
                            data.push(key + "=" + sessionStorage.getItem(key));
                        }

                        return data.join("\\n");
                    }
                    """
                )

                if storage_text:
                    collected_texts.append(storage_text)

                if response_tasks:
                    await asyncio.gather(
                        *response_tasks,
                        return_exceptions=True
                    )

            except Exception as error:
                print("抓取 codes.yar.gg 失敗")
                print(error)

            await browser.close()

        all_text = "\n".join(
            text
            for text in collected_texts
            if text
        )

        codes = CodesYar._extract_codes(all_text)

        print("codes.yar.gg All 分頁抓到：", codes)

        if not codes:
            return []

        return [
            CodesYarPost(
                id="codes-yar-all",
                url=CODES_YAR_URL,
                text="\n".join(codes),
                source="codes.yar.gg"
            )
        ]

    @staticmethod
    async def _capture_response(
        response,
        collected_texts: list[str]
    ) -> None:
        try:
            content_type = response.headers.get(
                "content-type",
                ""
            ).lower()

            url = response.url.lower()

            if "application/json" not in content_type and "text/plain" not in content_type:
                return

            if "codes.yar.gg" not in url and "yar.gg" not in url:
                return

            text = await response.text()

            if text:
                collected_texts.append(text)

        except Exception:
            return

    @staticmethod
    async def _safe_body_text(page) -> str:
        try:
            return await page.locator("body").inner_text()
        except Exception:
            return ""

    @staticmethod
    def _extract_codes(text: str) -> list[str]:
        if not text:
            return []

        upper_text = text.upper()

        candidates = CodesYar.CODE_PATTERN.findall(upper_text)

        result = []

        for code in candidates:
            code = code.strip().upper()

            if not code:
                continue

            if code in CodesYar.BLOCKLIST:
                continue

            if CodesYar._is_bad_code(code):
                continue

            if code not in result:
                result.append(code)

        return result

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        if len(code) < 5 or len(code) > 20:
            return True

        bad_keywords = [
            "SUBMIT",
            "CONTACT",
            "CANCEL",
            "CONFIRM",
            "REPORT",
            "ARCHIVE",
            "ACTIVE",
            "UNUSED",
            "USED",
            "EXPIRED",
            "COPY",
            "PREVIOUS",
            "NEXT",
            "WHERE",
            "WINDS",
            "MEET",
            "COUPON",
            "REDEEM",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
