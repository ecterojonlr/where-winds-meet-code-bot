from dataclasses import dataclass
import re
import urllib.request


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

    CODE_FIELD_PATTERN = re.compile(
        r"""(?:^|[,{]\s*)(?:"code"|'code'|code)\s*:\s*(["'])(.*?)\1""",
        re.DOTALL
    )

    STRING_PATTERN = re.compile(
        r"""(["'])([A-Za-z0-9]{5,20})\1"""
    )

    @staticmethod
    async def fetch() -> list[CodesYarPost]:
        print("開始抓取 codes.yar.gg 原始碼中的 codeEntries")
        print(CODES_YAR_URL)

        try:
            html = CodesYar._fetch_html()

            code_entries_block = CodesYar._extract_code_entries_block(
                html=html
            )

            if not code_entries_block:
                print("找不到 const codeEntries")
                return []

            codes = CodesYar._extract_codes_from_code_entries(
                code_entries_block
            )

            print("codes.yar.gg codeEntries 抓到：", codes)

            if not codes:
                return []

            return [
                CodesYarPost(
                    id="codes-yar-code-entries",
                    url=CODES_YAR_URL,
                    text="\n".join(codes),
                    source="codes.yar.gg"
                )
            ]

        except Exception as error:
            print("抓取 codes.yar.gg 失敗")
            print(error)
            return []

    @staticmethod
    def _fetch_html() -> str:
        request = urllib.request.Request(
            CODES_YAR_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:
            return response.read().decode(
                "utf-8",
                errors="replace"
            )

    @staticmethod
    def _extract_code_entries_block(html: str) -> str:
        match = re.search(
            r"\bconst\s+codeEntries\s*=",
            html
        )

        if not match:
            return ""

        start_search_index = match.end()

        array_start = html.find(
            "[",
            start_search_index
        )

        if array_start == -1:
            return ""

        depth = 0
        in_string = False
        string_quote = ""
        escape = False

        for index in range(array_start, len(html)):
            char = html[index]

            if in_string:
                if escape:
                    escape = False
                    continue

                if char == "\\":
                    escape = True
                    continue

                if char == string_quote:
                    in_string = False
                    string_quote = ""

                continue

            if char in ["'", '"', "`"]:
                in_string = True
                string_quote = char
                continue

            if char == "[":
                depth += 1

            elif char == "]":
                depth -= 1

                if depth == 0:
                    return html[array_start:index + 1]

        return ""

    @staticmethod
    def _extract_codes_from_code_entries(
        code_entries_block: str
    ) -> list[str]:
        result = []

        matches = CodesYar.CODE_FIELD_PATTERN.findall(
            code_entries_block
        )

        for _, raw_code in matches:
            code = CodesYar._clean_code(raw_code)

            if not CodesYar._is_valid_code(code):
                continue

            if code not in result:
                result.append(code)

        if result:
            return result

        fallback_matches = CodesYar.STRING_PATTERN.findall(
            code_entries_block
        )

        for _, raw_code in fallback_matches:
            code = CodesYar._clean_code(raw_code)

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

        if not CodesYar.CODE_PATTERN.match(code):
            return False

        return True
