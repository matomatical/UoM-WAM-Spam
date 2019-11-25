"""
pushbullet-based notifier

:author: CaviarChen and josephsurin
"""

import requests


class PushbulletNotifier:
    """
    Send notification using Pushbullet.
    https://www.pushbullet.com
    """
    def __init__(self, token: str) -> None:
        print("Configuring Pushbullet Notifier...")
        self.token = token

    def notify(self, subject: str, text: str) -> None:
        print("Sending Pushbullet notification...")
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "type": "note",
            "title": subject,
            "body": text
        }

        r = requests.post("https://api.pushbullet.com/v2/pushes",
            auth=(self.token, ''), json=data)
        if r.status_code != 200:
            raise Exception(r.status_code, r.text)
        
        print("Sent!", r.text)
