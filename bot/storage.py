import json
from pathlib import Path


DATA_FILE = Path("data/codes.json")


class Storage:
    @staticmethod
    def load_codes() -> list[str]:
        if not DATA_FILE.exists():
            return []

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_codes(codes: list[str]) -> None:
        DATA_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        clean_codes = sorted(set(codes))

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                clean_codes,
                file,
                indent=4,
                ensure_ascii=False
            )
