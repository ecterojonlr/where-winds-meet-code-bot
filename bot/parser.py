import re


class Parser:
    CODE_PATTERN = re.compile(
        r"^[A-Z0-9]{5,20}$"
    )

    BLOCKLIST = {
        # 帳號 / 來源
        "TERY0920",

        # Threads 介面文字
        "FOLLOW",
        "FOLLOWERS",
        "MENTION",
        "MENTIONS",
        "REPLIES",
        "REPLY",
        "MEDIA",
        "REPOST",
        "REPOSTS",
        "TRANSLATE",
        "THREADS",
        "INSTAGRAM",

        # Threads 頁尾 / 條款
        "THREADSTERMS",
        "PRIVACYPOLICY",
        "COOKIESPOLICY",
        "REPORTAPROBLEM",
        "SAYMOREWITHTHREADS",

        # 常見平台字
        "FACEBOOK",
        "TWITTER",
        "YOUTUBE",
        "DISCORD",

        # 常見普通字
        "CODE",
        "CODES",
        "REDEEM",
        "GIFT",

        # 已知誤判
        "105FOLLOWERS",
        "NKTTCPETYC",
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

            if Parser._is_bad_code(code):
                continue

            if not Parser.CODE_PATTERN.match(code):
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
        # 太短或太長不要
        if len(code) < 5 or len(code) > 20:
            return True

        # 含有明顯 Threads / UI 關鍵字不要
        bad_keywords = [
            "FOLLOW",
            "REPLY",
            "REPLIES",
            "REPOST",
            "MEDIA",
            "MENTION",
            "TRANSLATE",
            "THREADS",
            "TERMS",
            "PRIVACY",
            "COOKIES",
            "POLICY",
            "REPORT",
            "PROBLEM",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
