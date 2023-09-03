import linebot.v3.messaging as messaging


class Emoji(messaging.Emoji):
    def __init__(self, index: int, product_id: str, emoji_id: str) -> None:
        super().__init__(index=index, productId=product_id, emojiId=emoji_id)
