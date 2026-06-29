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
    
    if not posts:
        print("沒有抓到 Threads 貼文")
        return

    known_codes = set(Storage.load_codes())
    new_codes = []

    for post in posts:
        codes = Parser.extract_codes(post.text)

        for code in codes:
            if code not in known_codes:
                known_codes.add(code)
                new_codes.append(code)

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
