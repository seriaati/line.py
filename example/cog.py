from __future__ import annotations

from line import Bot, Cog, Context, command


class ExampleCog(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)

    @command
    async def hello(self, ctx: Context) -> None:
        """A simple command that replies with "Hello, world!"."""
        await ctx.reply_text("Hello, world!")

    @command
    async def plus(self, ctx: Context, num1: int, num2: int) -> None:
        """A command that takes two integer arguments."""
        await ctx.reply_text(f"{num1} + {num2} = {num1 + num2}")

    @command
    async def default_text(self, ctx: Context, text: str = "default") -> None:
        """A command that takes an optional text argument."""
        await ctx.reply_text(f"text = {text}")
