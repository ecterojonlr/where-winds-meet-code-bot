import re


class Parser:
    CODE_PATTERN = re.compile(
        r"^[A-Z0-9]{5,20}$"
    )

    BLOCKLIST = {
        "TERY0920",
        "THREADS",
        "INSTAGRAM",
        "FACEBOOK",
        "TWITTER",
        "YOUTUBE",
        "DISCORD",
        "REDEEM",
        "CODE",
        "CODES",
        "GIFT",
    }

    @staticmethod
    def extract_codes(text: str) -> list[str]:
        if not text:
            return []

        result = []

        for line in text.splitlines():
            code = Parser._clean_line(line)

            if not code:
                continue

            if code in Parser.BLOCKLIST:
                continue

            if not Parser.CODE_PATTERN.match(code):
                continue

            if code not in result:
                result.append(code)

        return result

    @staticmethod
    def _clean_line(line: str) -> str:
        line = line.strip().upper()

        # 移除常見包住序號的符號
        line = line.strip("`'\"[](){}<>：:，,。.!！")

        # 移除空白與連字號，避免格式化影響
        line = line.replace(" ", "")
        line = line.replace("-", "")

        return line
