# line.py
 Python 非阻塞式 LINE Messaging API 串接, 輕鬆快速的製作 LINE 機器人
 ⚠️ 此 package 目前僅供(我)個人使用, 所以並沒有 cover 全部的 API, 如果有其他人想用的話, 我再加

# 安裝
 ```
 pip install git+https://github.com/seriaati/line.py
 ```

# 快速入門
 ```py
 import asyncio
 from line import Bot, Cog, command, Context

 class MyCog(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
    
    @command
    async def hello(self, ctx: Context) -> None:
        await ctx.reply_text("Hello, world!")

 async def main():
    bot = Bot(channel_secret="YOUR_CHANNEL_SECRET", access_token="YOUR_ACCESS_TOKEN")
    bot.add_cog(MyCog(bot))
    await bot.run()
 ```

# 功能
 - 使用 aiohttp 及 asyncio, 完全非阻塞式運行 (async/await)
 - 底層使用 [LINE 官方 Python SDK](https://github.com/line/line-bot-sdk-python/)
 - 完整的 type hints ([PEP 484](https://peps.python.org/pep-0484/))
 - 簡單上手, 快速製作 LINE 機器人

# 文檔
 - [LINE Messasing API Docs](https://developers.line.biz/en/docs/messaging-api/)
 - [如何設定一個 LINE 機器人?](https://seraiati.notion.site/LINE-715e0c72e7c8481eb81ef19c8cf6ddfb?pvs=4)

# 其他
## LINE 已經有 SDK 了, 為什麼還要寫 line.py?
 - v3 的 SDK 可能因為是從 API 自動生成 model 的關係, 有非常糟糕的 typing 問題, 使用 line.py 完全不會遇到奇怪的紅線跟需要大量使用 type: ignore 的問題
 - 學習難度高, 不易使用, 不適合新手
 - 沒有一個快速新增指令的方法, 導致程式碼很冗長
## 你是不是抄襲 discord.py?
 對。  
 但是 discord.py 的程式碼太高深了我看不懂, 所以只是參考概念 (例如 cog, 一些 function 的名稱, 新增指令的方式), 然後慢慢刻出來 line.py。

# 聯絡
 有疑問可以加我 Discord：[@seria_ati](https://discord.com/users/410036441129943050)