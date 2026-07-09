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
        "",
        "SEARCH",
        "TIPJAR",
        "COPY",
        "COPIED",
        "USED",
        "EXPIRED",
        "UNUSED",
        "ACTIVE",
        "CODE",
        "CODES",
        "SUBMIT",
        "CONTACT",
        "REPORT",
        "FILTER",
        "ALL",
        "WHERE",
        "WINDS",
        "MEET",
        "WWM",
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
                    "height": 2400
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            )

            try:
                print("開始抓取 codes.yar.gg 表格 input 序號")
                print(CODES_YAR_URL)

                await page.goto(
                    CODES_YAR_URL,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(5000)

                await CodesYar._click_all_tab(page)

                await page.wait_for_timeout(2000)

                # 捲到底，確保表格內容都有載入
                await CodesYar._scroll_to_bottom(page)

                # 只抓 input.value
                codes = await CodesYar._extract_input_codes(page)

            except Exception as error:
                print("抓取 codes.yar.gg 失敗")
                print(error)

            await browser.close()

        clean_codes = CodesYar._clean_codes(codes)

        print("codes.yar.gg 表格 input 抓到：", clean_codes)

        if not clean_codes:
            return []

        return [
            CodesYarPost(
                id="codes-yar-input-table",
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
    async def _scroll_to_bottom(page) -> None:
        previous_height = 0

        for _ in range(20):
            current_height = await page.evaluate(
                "document.body.scrollHeight"
            )

            if current_height == previous_height:
                break

            previous_height = current_height

            await page.mouse.wheel(0, 2500)
            await page.wait_for_timeout(500)

        await page.wait_for_timeout(1000)

    @staticmethod
    async def _extract_input_codes(page) -> list[str]:
        raw_values = await page.evaluate(
            """
            () => {
                const values = [];

                const inputs = Array.from(
                    document.querySelectorAll("input")
                );

                for (const input of inputs) {
                    const value = String(input.value || "").trim();

                    if (!value) {
                        continue;
                    }

                    values.push(value);
                }

                return values;
            }
            """
        )

        result = []

        for value in raw_values:
            code = CodesYar._clean_code(value)

            if CodesYar._is_valid_code(code):
                result.append(code)

        return result

    @staticmethod
    def _clean_codes(codes: list[str]) -> list[str]:
        result = []

        for code in codes:
            clean_code = CodesYar._clean_code(code)

            if not CodesYar._is_valid_code(clean_code):
                continue

            if clean_code not in result:
                result.append(clean_code)

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

        if not CodesYar.CODE_PATTERN.match(code):
            return False

        if CodesYar._is_bad_code(code):
            return False

        return True

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        if len(code) < 5 or len(code) > 20:
            return True

        # 排除搜尋框、頁面提示、數量提示
        if re.fullmatch(r"\d+LEFT", code):
            return True

        if re.fullmatch(r"CODE\d+OF\d+", code):
            return True

        if re.fullmatch(r"\d+(LEFT|USED|EXPIRED|CODES|CODE)", code):
            return True

        bad_keywords = [
            "SEARCH",
            "TIPJAR",
            "COPY",
            "COPIED",
            "SUBMIT",
            "CONTACT",
            "REPORT",
            "FILTER",
            "ACTIVE",
            "UNUSED",
            "USED",
            "EXPIRED",
            "CODE",
            "CODES",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
