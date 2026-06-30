import discord


class DiscordBot:

    def __init__(
        self,
        token: str,
        channel_ids: list[int]
    ):

        self.token = token
        self.channel_ids = channel_ids

        self.client = discord.Client(
            intents=discord.Intents.default()
        )

    async def send_codes(
        self,
        codes: list[str],
        date: str
    ):

        @self.client.event
        async def on_ready():

            message = (
                "🎁 **發現新的燕雲十六聲兌換碼！**\n\n"
                + "\n".join(
                    f" `{code}`"
                    for code in codes
                )
                + f"\n\n📅 {date}"
            )

            success = 0

            for channel_id in self.channel_ids:

                channel = self.client.get_channel(
                    channel_id
                )

                if channel is None:

                    print(
                        f"找不到頻道：{channel_id}"
                    )

                    continue

                try:

                    await channel.send(message)

                    success += 1

                    print(
                        f"已發送到：{channel_id}"
                    )

                except Exception as e:

                    print(e)

            print(
                f"成功發送 {success}/{len(self.channel_ids)} 個頻道"
            )

            await self.client.close()

        await self.client.start(self.token)
