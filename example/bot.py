import asyncio
import os

from dotenv import load_dotenv

from line import Bot

load_dotenv()


async def main() -> None:
    channel_secret = os.getenv("CHANNEL_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    if not (channel_secret and access_token):
        raise RuntimeError("Channel secret and access token must be provided")
    bot = Bot(channel_secret=channel_secret, access_token=access_token)
    bot.add_cog("example.cog")
    await bot.run()


asyncio.run(main())
