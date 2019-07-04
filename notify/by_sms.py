"""
pushbullet-based SMS notifier

:author: CaviarChen and josephsurin
"""

import requests

class PushBulletNotifier:
    """
    Send notification using PushBullet.
    https://www.pushbullet.com
    """
    def __init__(self, token: str) -> None:
        self.token = token

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "type": "note",
            "title": subject,
            "body": text
        }

        r = requests.post("https://api.pushbullet.com/v2/pushes",
            auth=(self.token, ''), json=data)
        if r.status_code == 200:
            print("Sent!", r.text)
        else:
            raise Exception(r.status_code, r.text)
