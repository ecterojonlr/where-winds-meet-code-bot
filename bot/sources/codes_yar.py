from dataclasses import dataclass
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
        r"^[A-Z0-9]{5,20}$"
    )

    BLOCKLIST = {
        # codes.yar.gg 新增誤判
        "TIPJAR",

        # codes.yar.gg 介面文字
        "TRACK",
        "CLICK",
        "MARKED",
        "BELOW",
        "PASTE",
        "REPEAT",
        "NEVER",
        "ADDED",
        "BUILD",
        "TUTORIAL",
        "BROWSER",
        "SUBMISSION",

        # 語言 / 網站文字
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

        # 常見 UI 字串
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

        # 遊戲名稱 / 網站名稱
        "WHERE",
        "WINDS",
        "MEET",
        "WWM",
        "YARGG",
    }

    @staticmethod
    async def fetch() -> list[CodesYarPost]:
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

            body_text = ""

            try:
                print("開始抓取 codes.yar.gg 的 All 分頁")
                print(CODES_YAR_URL)

                await page.goto(
                    CODES_YAR_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(5000)

                await CodesYar._click_all_tab(page)

                await page.wait_for_timeout(2000)

                body_text = await CodesYar._safe_body_text(page)

            except Exception as error:
                print("抓取 codes.yar.gg 失敗")
                print(error)

            await browser.close()

        codes = CodesYar._extract_codes(body_text)

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
    async def _click_all_tab(page) -> None:
        try:
            await page.get_by_role(
                "button",
                name="All",
                exact=True
            ).click(timeout=3000)
            return
        except Exception:
            pass

        try:
            await page.get_by_role(
                "tab",
                name="All",
                exact=True
            ).click(timeout=3000)
            return
        except Exception:
            pass

        try:
            await page.get_by_text(
                "All",
                exact=True
            ).click(timeout=3000)
            return
        except Exception:
            print("codes.yar.gg 找不到 All 按鈕，使用目前頁面內容")

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

        result = []

        for line in text.splitlines():
            code = CodesYar._clean_line(line)

            if not code:
                continue

            if code in CodesYar.BLOCKLIST:
                continue

            if CodesYar._is_bad_code(code):
                continue

            if not CodesYar.CODE_PATTERN.match(code):
                continue

            if code not in result:
                result.append(code)

        return result

    @staticmethod
    def _clean_line(line: str) -> str:
        line = line.strip().upper()

        line = line.strip("`'\"[](){}<>：:，,。.!！")

        line = line.replace(" ", "")
        line = line.replace("-", "")

        return line

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        if len(code) < 5 or len(code) > 20:
            return True

        # 排除 ISO 時間片段，例如 09T02、09T09
        if re.fullmatch(r"\d{2}T\d{2}", code):
            return True

        # 排除 codes.yar.gg 的數量提示，例如 79LEFT
        if re.fullmatch(r"\d+LEFT", code):
            return True

        # 排除 codes.yar.gg 的頁面提示，例如 CODE1OF79
        if re.fullmatch(r"CODE\d+OF\d+", code):
            return True

        # 排除純數字 + 常見 UI 詞
        if re.fullmatch(r"\d+(LEFT|USED|EXPIRED|CODES|CODE)", code):
            return True

        bad_keywords = [
            "TIPJAR",
            "JAR",

            "TRACK",
            "CLICK",
            "MARK",
            "BELOW",
            "PASTE",
            "REPEAT",
            "NEVER",
            "ADDED",
            "BUILD",
            "TUTORIAL",
            "BROWSER",
            "SUBMISSION",

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
            "COPIED",
            "PREVIOUS",
            "NEXT",
            "LEFT",
            "WHERE",
            "WINDS",
            "MEET",
            "COUPON",
            "REDEEM",
            "CODE",
            "CODES",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
