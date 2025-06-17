from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from line import Bot

load_dotenv()


async def main() -> None:
    """Runs the bot."""
    channel_secret = os.getenv("CHANNEL_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    if not (channel_secret and access_token):
        msg = "Channel secret and access token must be provided"
        raise RuntimeError(msg)
    bot = Bot(channel_secret=channel_secret, access_token=access_token)
    bot.add_cog("example.cog")
    await bot.run()


asyncio.run(main())
