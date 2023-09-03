import linebot.v3.messaging as messaging


class Emoji(messaging.Emoji):
    def __init__(self, product_id: str, emoji_id: str) -> None:
        self.product_id = product_id
        self.emoji_id = emoji_id
