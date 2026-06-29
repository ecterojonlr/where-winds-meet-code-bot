import asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from bot.discord_bot import DiscordBot
from bot.parser import Parser
from bot.storage import Storage
from bot.sources.threads import Threads


TOKEN = os.environ["DISCORD_TOKEN"]


async def main():
    channel_ids = Storage.load_channels()

    if not channel_ids:
        print("沒有設定任何 Discord 頻道，請檢查 data/channels.json")
        return

    posts = await Threads.fetch()

    if not posts:
        print("沒有抓到 Threads 貼文")
        return

    known_codes = set(Storage.load_codes())
    new_codes = []

    for index, post in enumerate(posts):
        print("=" * 50)
        print(f"檢查第 {index + 1} 篇貼文")

        codes = Parser.extract_codes(post.text)

        print("本篇抓到：", codes)

        for code in codes:
            if code not in known_codes:
                known_codes.add(code)
                new_codes.append(code)
            else:
                print(f"已存在：{code}")

    if not new_codes:
        print("沒有新的兌換碼")
        return

    Storage.save_codes(list(known_codes))

    taipei_time = datetime.now(
        ZoneInfo("Asia/Taipei")
    ).strftime("%Y/%m/%d %H:%M")

    bot = DiscordBot(
        token=TOKEN,
        channel_ids=channel_ids
    )

    await bot.send_codes(
        codes=new_codes,
        date=f"{taipei_time} GMT+8"
    )


if __name__ == "__main__":
    asyncio.run(main())
