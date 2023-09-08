class Emoji:
    """
    https://developers.line.biz/en/docs/messaging-api/emoji-list/#line-emoji-definitions
    """

    def __init__(self, product_id: str, emoji_id: str) -> None:
        self.product_id = product_id
        self.emoji_id = emoji_id
