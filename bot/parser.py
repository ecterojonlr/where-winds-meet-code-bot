import re


class Parser:
    CODE_PATTERN = re.compile(
        r"\b(?=[A-Z0-9]{5,20}\b)(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{5,20}\b"
    )

    BLOCKLIST = {
        "TERY0920",
    }

    @staticmethod
    def extract_codes(text: str) -> list[str]:
        if not text:
            return []

        text = text.upper()

        codes = Parser.CODE_PATTERN.findall(text)

        result = []

        for code in codes:
            if code in Parser.BLOCKLIST:
                continue

            if code not in result:
                result.append(code)

        return result
