import asyncio
import os
from datetime import datetime

from bot.discord_bot import DiscordBot
from bot.parser import Parser
from bot.storage import Storage
from bot.sources.threads import Threads


TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])


async def main():
    latest_post = await Threads.fetch_latest()

    if latest_post is None:
        print("沒有抓到最新貼文")
        return

    last_post_id = Storage.load_latest_post_id()

    print(f"上次記錄貼文 ID：{last_post_id}")
    print(f"這次最新貼文 ID：{latest_post.id}")

    if latest_post.id == last_post_id:
        print("最新貼文沒有變，不檢查兌換碼")
        return

    codes = Parser.extract_codes(latest_post.text)

    print("本篇抓到的兌換碼：", codes)

    if not codes:
        print("最新貼文沒有兌換碼")
        Storage.save_latest_post_id(latest_post.id)
        return

    known_codes = set(Storage.load_codes())
    new_codes = []

    for code in codes:
        if code not in known_codes:
            known_codes.add(code)
            new_codes.append(code)
        else:
            print(f"已存在：{code}")

    Storage.save_latest_post_id(latest_post.id)

    if not new_codes:
        print("沒有新的兌換碼")
        return

    Storage.save_codes(list(known_codes))

    bot = DiscordBot(
        token=TOKEN,
        channel_id=CHANNEL_ID
    )

    await bot.send_codes(
        codes=new_codes,
        date=datetime.now().strftime("%Y/%m/%d")
    )


if __name__ == "__main__":
    asyncio.run(main())
