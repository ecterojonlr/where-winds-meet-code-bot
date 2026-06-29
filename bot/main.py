import asyncio
import os
from datetime import datetime

from bot.discord_bot import DiscordBot

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])


async def main():
    bot = DiscordBot(TOKEN, CHANNEL_ID)

    await bot.send_codes(
        ["TEST123"],
        datetime.now().strftime("%Y/%m/%d"),
    )


if __name__ == "__main__":
    asyncio.run(main())
