"""
Telegram bot-based telegram notifier

:author: blueset
"""

import requests


class TelegramBotNotifier:
    """
    Send notification using Telegram Bot API.

    Telegram bot can be created with @BotFather (https://t.me/botfather).
    """
    def __init__(self) -> None:
        print("Configuring Telegram Bot Notifier...")
        token = input("Access token (see README): ")
        self.entry_point = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat = input("Destination (see README): ")

    def notify(self, subject: str, text: str) -> None:
        print("Sending Telegram Bot notification...")
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "text": f"<b>{subject}</b>\n\n{text}",
            "chat_id": self.chat,
            "parse_mode": "html",
            "disable_web_page_preview": True
        }

        r = requests.post(self.entry_point, json=data)
        if r.status_code != 200:
            raise Exception(r.status_code, r.text)
        
        print("Sent!", r.text)
