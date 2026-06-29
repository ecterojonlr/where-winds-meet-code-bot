import json
from pathlib import Path

DATA_FILE = Path("data/codes.json")


class Storage:

    @staticmethod
    def load_codes() -> list[str]:
        if not DATA_FILE.exists():
            return []

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_codes(codes: list[str]) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                sorted(codes),
                file,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def is_new(code: str) -> bool:
        codes = Storage.load_codes()
        return code not in codes

    @staticmethod
    def add_codes(new_codes: list[str]) -> None:
        codes = Storage.load_codes()

        changed = False

        for code in new_codes:
            if code not in codes:
                codes.append(code)
                changed = True

        if changed:
            Storage.save_codes(codes)
