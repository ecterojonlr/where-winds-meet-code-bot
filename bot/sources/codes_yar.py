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
        codes: list[str] = []

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

            try:
                print("開始抓取 codes.yar.gg 下方表格序號")
                print(CODES_YAR_URL)

                await page.goto(
                    CODES_YAR_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(5000)

                # 點擊「全部 / All」分頁
                await CodesYar._click_all_tab(page)

                await page.wait_for_timeout(2000)

                # 往下捲，確保下方表格已經載入
                for _ in range(5):
                    await page.mouse.wheel(0, 1200)
                    await page.wait_for_timeout(500)

                # 只抓下方表格中的序號，不抓最上方單一展示序號
                codes = await CodesYar._extract_table_codes(page)

            except Exception as error:
                print("抓取 codes.yar.gg 失敗")
                print(error)

            await browser.close()

        clean_codes = CodesYar._clean_codes(codes)

        print("codes.yar.gg 表格抓到：", clean_codes)

        if not clean_codes:
            return []

        return [
            CodesYarPost(
                id="codes-yar-table",
                url=CODES_YAR_URL,
                text="\n".join(clean_codes),
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
    async def _extract_table_codes(page) -> list[str]:
        """
        只抓下方表格 / 清單裡的序號。
        不抓最上方大型展示中的單一序號。
        """

        codes: list[str] = []

        # 這段直接從 DOM 裡找像「下方表格序號欄位」的 input/button/div
        raw_codes = await page.evaluate(
            """
            () => {
                const results = [];

                const elements = Array.from(
                    document.querySelectorAll("input, button, div, span")
                );

                for (const el of elements) {
                    const rect = el.getBoundingClientRect();

                    // 排除最上方展示區
                    // 只抓頁面中段以下的內容，也就是下方表格區
                    if (rect.top < 430) {
                        continue;
                    }

                    let text = "";

                    if (el.tagName === "INPUT") {
                        text = el.value || "";
                    } else {
                        text = el.innerText || el.textContent || "";
                    }

                    text = text.trim();

                    if (!text) {
                        continue;
                    }

                    results.push(text);
                }

                return results;
            }
            """
        )

        for item in raw_codes:
            for line in str(item).splitlines():
                code = CodesYar._clean_line(line)

                if CodesYar._is_valid_code(code):
                    codes.append(code)

        return codes

    @staticmethod
    def _clean_codes(codes: list[str]) -> list[str]:
        result = []

        for code in codes:
            code = CodesYar._clean_line(code)

            if not CodesYar._is_valid_code(code):
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
    def _is_valid_code(code: str) -> bool:
        if not code:
            return False

        if code in CodesYar.BLOCKLIST:
            return False

        if not CodesYar.CODE_PATTERN.match(code):
            return False

        if CodesYar._is_bad_code(code):
            return False

        return True

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        if len(code) < 5 or len(code) > 20:
            return True

        # 排除 ISO 時間片段，例如 09T02、09T09
        if re.fullmatch(r"\d{2}T\d{2}", code):
            return True

        # 排除數量提示，例如 79LEFT
        if re.fullmatch(r"\d+LEFT", code):
            return True

        # 排除頁面提示，例如 CODE1OF79
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
