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
        r"\b[A-Z0-9]{5,20}\b"
    )

    BLOCKLIST = {
        "TIPJAR",
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
        body_text = ""

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
                    "height": 2400
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            )

            try:
                print("開始抓取 codes.yar.gg 可用序號區塊")
                print(CODES_YAR_URL)

                await page.goto(
                    CODES_YAR_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(5000)

                await CodesYar._click_all_tab(page)

                await page.wait_for_timeout(2000)

                # 捲到頁面底部，讓所有表格內容都載入
                previous_height = 0

                for _ in range(20):
                    current_height = await page.evaluate(
                        "document.body.scrollHeight"
                    )

                    if current_height == previous_height:
                        break

                    previous_height = current_height

                    await page.mouse.wheel(0, 2000)
                    await page.wait_for_timeout(500)

                body_text = await CodesYar._safe_body_text(page)

            except Exception as error:
                print("抓取 codes.yar.gg 失敗")
                print(error)

            await browser.close()

        usable_section = CodesYar._extract_usable_section(body_text)

        codes = CodesYar._extract_codes(usable_section)

        print("codes.yar.gg 可用序號抓到：", codes)

        if not codes:
            return []

        return [
            CodesYarPost(
                id="codes-yar-usable-section",
                url=CODES_YAR_URL,
                text="\n".join(codes),
                source="codes.yar.gg"
            )
        ]

    @staticmethod
    async def _click_all_tab(page) -> None:
        tab_names = [
            "全部",
            "All",
        ]

        for tab_name in tab_names:
            try:
                await page.get_by_role(
                    "button",
                    name=tab_name,
                    exact=True
                ).click(timeout=3000)

                print(f"已切換分頁：{tab_name}")

                return

            except Exception:
                pass

            try:
                await page.get_by_text(
                    tab_name,
                    exact=True
                ).click(timeout=3000)

                print(f"已切換分頁：{tab_name}")

                return

            except Exception:
                pass

        print("codes.yar.gg 找不到全部 / All 分頁，使用目前頁面")

    @staticmethod
    async def _safe_body_text(page) -> str:
        try:
            return await page.locator("body").inner_text()
        except Exception:
            return ""

    @staticmethod
    def _extract_usable_section(text: str) -> str:
        if not text:
            return ""

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        start_keywords = [
            "可用兌換碼",
            "可用兑换码",
            "AVAILABLE CODES",
            "USABLE CODES",
            "ACTIVE CODES",
        ]

        stop_keywords = [
            "過期兌換碼",
            "过期兑换码",
            "EXPIRED CODES",
            "ARCHIVED CODES",
            "CONFIRMED EXPIRED",
        ]

        start_index = -1
        stop_index = len(lines)

        for index, line in enumerate(lines):
            upper_line = line.upper()

            if any(keyword.upper() in upper_line for keyword in start_keywords):
                start_index = index
                break

        if start_index == -1:
            print("找不到可用兌換碼區塊，改用整頁文字")
            return "\n".join(lines)

        for index in range(start_index + 1, len(lines)):
            upper_line = lines[index].upper()

            if any(keyword.upper() in upper_line for keyword in stop_keywords):
                stop_index = index
                break

        section_lines = lines[start_index:stop_index]

        return "\n".join(section_lines)

    @staticmethod
    def _extract_codes(text: str) -> list[str]:
        if not text:
            return []

        candidates = CodesYar.CODE_PATTERN.findall(
            text.upper()
        )

        result = []

        for code in candidates:
            code = CodesYar._clean_code(code)

            if not CodesYar._is_valid_code(code):
                continue

            if code not in result:
                result.append(code)

        return result

    @staticmethod
    def _clean_code(code: str) -> str:
        code = str(code).strip().upper()

        code = code.strip("`'\"[](){}<>：:，,。.!！")

        code = code.replace(" ", "")
        code = code.replace("-", "")

        return code

    @staticmethod
    def _is_valid_code(code: str) -> bool:
        if not code:
            return False

        if code in CodesYar.BLOCKLIST:
            return False

        if not re.fullmatch(r"[A-Z0-9]{5,20}", code):
            return False

        if CodesYar._is_bad_code(code):
            return False

        return True

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        if len(code) < 5 or len(code) > 20:
            return True

        if re.fullmatch(r"\d{2}T\d{2}", code):
            return True

        if re.fullmatch(r"\d+LEFT", code):
            return True

        if re.fullmatch(r"CODE\d+OF\d+", code):
            return True

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
            "COUPON",
            "REDEEM",
            "CODE",
            "CODES",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
