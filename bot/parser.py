import re


class Parser:

    CODE_PATTERN = re.compile(
        r"\b[A-Z0-9]{5,20}\b"
    )

    @staticmethod
    def extract_codes(text: str) -> list[str]:

        codes = Parser.CODE_PATTERN.findall(
            text.upper()
        )

        result = []

        for code in codes:
            if code not in result:
                result.append(code)

        return result
