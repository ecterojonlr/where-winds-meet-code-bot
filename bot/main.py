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

    posts = Threads.fetch()

    new_codes = []

    for post in posts:

        codes = Parser.extract_codes(post)

        for code in codes:

            if Storage.is_new(code):
                new_codes.append(code)

    if not new_codes:

        print("沒有新的兌換碼")

        return

    Storage.add_codes(new_codes)

    bot = DiscordBot(
        TOKEN,
        CHANNEL_ID
    )

    await bot.send_codes(
        new_codes,
        datetime.now().strftime("%Y/%m/%d")
    )


if __name__ == "__main__":

    asyncio.run(main())
