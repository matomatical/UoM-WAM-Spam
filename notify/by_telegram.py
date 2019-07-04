"""
Telegram bot-based telegram notifier

:author: blueset
"""

from inspect import cleandoc

import requests

def setup():
    print(cleandoc("""
    Setup Telegram bot notifications
    ================================

    Please provide your Telegram bot access token. Your token can be 
    obtained from @BotFather (https://t.me/botfather), and should in the 
    following format:

        123456789:AaBbCcDdEeFfGgHhIiJjKkLlMm
    
    If you don't yet have a bot, you can make one with @BotFather.
    """))
    token = input("Access token: ")
    
    print(cleandoc("""

    Please provide your destination of messages. This should be:

        - a numerical ID of a user, group or channel, which can be obtained
          with bots like @GetIDBot (https://t.me/getidbot)
        - Username of a *public group*, e.g. @lyricova
    
    """))
    chat = input("Destination: ")

    print(cleandoc("""

    Now you are all set. Please make sure to send at least a message to 
    the bot if you just created one, and ensure that the bot is able to
    deliver message to your destination.
    """))

    return (token, chat)


class TelegramBotNotifier:
    """
    Send notification using Telegram Bot API.

    Telegram bot can be created with @BotFather (https://t.me/botfather).
    """
    def __init__(self, token: str, chat: str) -> None:
        self.token = token
        self.chat = chat
        self.entry_point = f"https://api.telegram.org/bot{token}/sendMessage"

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "text": f"<b>{subject}</b>\n\n{text}",
            "chat_id": self.chat,
            "parse_mode": "html",
            "disable_web_page_preview": True
        }

        r = requests.post(self.entry_point, json=data)
        if r.status_code == 200:
            print("Sent!", r.text)
        else:
            raise Exception(r.status_code, r.text)
