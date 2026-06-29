import json
from pathlib import Path


CODES_FILE = Path("data/codes.json")
CHANNELS_FILE = Path("data/channels.json")


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

        # 保持發現順序，只移除重複
        clean_codes = list(dict.fromkeys(codes))

        with open(CODES_FILE, "w", encoding="utf-8") as file:
            json.dump(
                clean_codes,
                file,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def load_channels() -> list[int]:
        if not CHANNELS_FILE.exists():
            print("找不到 data/channels.json")
            return []

        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print("channels.json 格式錯誤，必須是 list")
                return []

            channel_ids = []

            for item in data:
                if isinstance(item, int):
                    channel_ids.append(item)

                elif isinstance(item, str) and item.strip().isdigit():
                    channel_ids.append(int(item.strip()))

                elif isinstance(item, dict) and "channel_id" in item:
                    channel_ids.append(int(item["channel_id"]))

            return list(dict.fromkeys(channel_ids))

        except Exception as error:
            print("讀取 channels.json 失敗")
            print(error)
            return []

    @staticmethod
    def save_channels(channel_ids: list[int]) -> None:
        CHANNELS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        clean_channels = list(dict.fromkeys(channel_ids))

        with open(CHANNELS_FILE, "w", encoding="utf-8") as file:
            json.dump(
                clean_channels,
                file,
                indent=4,
                ensure_ascii=False
            )
