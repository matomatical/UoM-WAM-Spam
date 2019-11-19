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
    def __init__(self, apikey: str) -> None:
        print("Configuring Server Chan Notifier...")
        self.api = f"https://sc.ftqq.com/{apikey}.send"

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
