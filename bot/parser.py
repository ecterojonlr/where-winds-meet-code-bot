import re


class Parser:
    CODE_PATTERN = re.compile(
        r"\b(?=[A-Z0-9]{10}\b)(?=.*[A-Z])(?=.*\d)[A-Z0-9]{10}\b"
    )

    @staticmethod
    def extract_codes(text: str) -> list[str]:
        if not text:
            return []

        text = text.upper()

        codes = Parser.CODE_PATTERN.findall(text)

        result = []

        for code in codes:
            if code not in result:
                result.append(code)

        return result
