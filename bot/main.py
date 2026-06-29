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
    posts = await Threads.fetch()

    print(f"抓到 Threads 貼文數量：{len(posts)}")

    known_codes = set(Storage.load_codes())
    print(f"目前已記錄兌換碼數量：{len(known_codes)}")

    new_codes = []

    for index, post in enumerate(posts):
        print("=" * 50)
        print(f"第 {index + 1} 篇貼文")
        print(post.text[:1000])

        codes = Parser.extract_codes(post.text)

        print("本篇抓到的兌換碼：", codes)

        for code in codes:
            if code not in known_codes:
                print("新兌換碼：", code)
                known_codes.add(code)
                new_codes.append(code)
            else:
                print("已存在：", code)

    print("最後準備發送的新兌換碼：", new_codes)

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
