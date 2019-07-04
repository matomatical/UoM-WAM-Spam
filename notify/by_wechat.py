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
    def __init__(self, token: str) -> None:
        self.api = f"https://sc.ftqq.com/{token}.send"

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")
        
        data = {
                "text": subject,
                "desp": text
        }
        r = requests.get(self.api, params=data)
        if r.json()["errno"] == 0:
            print("Sent!", r.text)
        else:
            raise Exception(r.text)
