import json
from pathlib import Path


CODES_FILE = Path("data/codes.json")
LATEST_POST_FILE = Path("data/latest_post.json")


class Storage:

    @staticmethod
    def load_codes() -> list[str]:
        if not CODES_FILE.exists():
            return []

        try:
            with open(CODES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_codes(codes: list[str]) -> None:
        CODES_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        clean_codes = sorted(set(codes))

        with open(CODES_FILE, "w", encoding="utf-8") as file:
            json.dump(
                clean_codes,
                file,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def load_latest_post_id() -> str | None:
        if not LATEST_POST_FILE.exists():
            return None

        try:
            with open(LATEST_POST_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get("id")

        except json.JSONDecodeError:
            return None

    @staticmethod
    def save_latest_post_id(post_id: str) -> None:
        LATEST_POST_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(LATEST_POST_FILE, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "id": post_id
                },
                file,
                indent=4,
                ensure_ascii=False
            )
