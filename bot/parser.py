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

        # 請求過於頻繁 / 限流 / 錯誤頁面
        "TOOFREQUENT",
        "FREQUENT",
        "TOOMANYREQUESTS",
        "RATELIMIT",
        "RATELIMITED",
        "TRYAGAIN",
        "TRYAGAINLATER",
        "PLEASETRYAGAIN",
        "PLEASETRYAGAINLATER",
        "REQUESTFAILED",
        "REQUESTERROR",
        "REQUESTTIMEOUT",
        "TIMEOUT",
        "ERROR",
        "SERVERERROR",
        "INTERNALSERVERERROR",
        "BADGATEWAY",
        "SERVICEUNAVAILABLE",
        "GATEWAYTIMEOUT",
        "UNAVAILABLE",
        "FORBIDDEN",
        "ACCESSDENIED",
        "ACCESSFORBIDDEN",
        "DENIED",
        "BLOCKED",
        "REQUESTBLOCKED",
        "TOOFAST",
        "WAIT",
        "PLEASEWAIT",
        "WAITAMOMENT",
        "HOLDON",
        "RETRY",
        "RETRYLATER",
        "FAILED",
        "FAILURE",
        "INVALIDREQUEST",
        "NOTFOUND",
        "NETWORKERROR",
        "CONNECTIONERROR",
        "CONNECTIONFAILED",

        # Cloudflare / 驗證 / 防刷頁面
        "CLOUDFLARE",
        "CHECKINGBROWSER",
        "JUSTAMOMENT",
        "VERIFYHUMAN",
        "HUMANVERIFICATION",
        "SECURITYCHECK",
        "CHALLENGE",
        "CHALLENGEREQUIRED",
        "CAPTCHA",
        "CAPTCHAREQUIRED",
        "DDOSPROTECTION",
        "NGINX",
        "CFRAY",
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

        # 移除常見包住序號的符號
        line = line.strip("`'\"[](){}<>：:，,。.!！")

        # 移除空白與連字號，避免格式化影響
        line = line.replace(" ", "")
        line = line.replace("-", "")

        return line

    @staticmethod
    def _is_bad_code(code: str) -> bool:
        # 太短或太長不要
        if len(code) < 5 or len(code) > 20:
            return True

        # 排除 ISO 時間片段，例如 09T02、09T09
        if re.fullmatch(r"\d{2}T\d{2}", code):
            return True

        # 排除 codes.yar.gg 數量提示，例如 79LEFT
        if re.fullmatch(r"\d+LEFT", code):
            return True

        # 排除 codes.yar.gg 頁面提示，例如 CODE1OF79
        if re.fullmatch(r"CODE\d+OF\d+", code):
            return True

        # 排除數字 + UI 詞
        if re.fullmatch(r"\d+(LEFT|USED|EXPIRED|CODES|CODE)", code):
            return True

        # 排除像網站內部 ID / hash 的純十六進位字串
        # 例如 4E9E9ADC30A5、A885EB99B78F、1B32379F
        if re.fullmatch(r"(?=.*[A-F])(?=.*\d)[A-F0-9]{8,20}", code):
            return True

        bad_keywords = [
            # Threads / 社群平台介面
            "FOLLOW",
            "FOLLOWER",
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

            # codes.yar.gg 介面 / 說明文字
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

            # 限流 / 錯誤 / 防刷提示
            "FREQUENT",
            "TOOMANY",
            "REQUEST",
            "RATELIMIT",
            "LIMITED",
            "TRYAGAIN",
            "LATER",
            "TIMEOUT",
            "ERROR",
            "FAILED",
            "FAILURE",
            "SERVER",
            "GATEWAY",
            "UNAVAILABLE",
            "FORBIDDEN",
            "ACCESS",
            "DENIED",
            "BLOCKED",
            "RETRY",
            "WAIT",
            "CLOUDFLARE",
            "VERIFY",
            "HUMAN",
            "SECURITY",
            "CHALLENGE",
            "CAPTCHA",
            "DDOS",
            "NGINX",
            "CFRAY",
        ]

        for keyword in bad_keywords:
            if keyword in code:
                return True

        return False
