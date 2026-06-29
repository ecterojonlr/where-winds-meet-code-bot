import discord


class DiscordBot:
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id
        self.client = discord.Client(
            intents=discord.Intents.default()
        )

    async def send_codes(self, codes: list[str], date: str):
        @self.client.event
        async def on_ready():
            channel = self.client.get_channel(self.channel_id)

            if channel is None:
                print("找不到 Discord 頻道")
                await self.client.close()
                return

            message = (
                "🎁 **發現新的燕雲十六聲兌換碼！**\n\n"
                + "\n".join(f"`{code}`" for code in codes)
                + f"\n\n📅 {date}"
            )

            await channel.send(message)
            await self.client.close()

        await self.client.start(self.token)
