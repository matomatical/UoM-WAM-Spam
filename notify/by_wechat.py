"""
serverchan-based wechat notifier

:author: CaviarChen
"""

import requests


class ServerChanNotifier:
    """
    Send notification to wechat using ServerChan.
    https://sc.ftqq.com
    """
    def __init__(self) -> None:
        print("Configuring Server Chan Notifier...")
        token = input("API Key (see README): ")
        self.api = f"https://sc.ftqq.com/{token}.send"

    def notify(self, subject: str, text: str) -> None:
        print("Sending We Chat message...")
        print("Message:", '"""', text, '"""', sep="\n")
        
        data = {
                "text": subject,
                "desp": text
        }
        r = requests.get(self.api, params=data)
        if r.json()["errno"] != 0:
            raise Exception(r.text)
        
        print("Sent!", r.text)
