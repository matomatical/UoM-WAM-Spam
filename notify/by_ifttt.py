"""
IFTTT Webbhook-based notifier

:author: blueset
"""

import requests


class IFTTTWebhookNotifier:
    """
    Send notification using IFTTT WebHook.

    Messages will be sent in "wam-spam" event, with "value1" as the title,
    and "value2" as the body text.
    """

    def __init__(self, key: str) -> None:
        print("Configuring IFTTT Webhook Notifier...")
        self.entry_point = f"https://maker.ifttt.com/trigger/wam-spam/with/key/{key}"

    def notify(self, subject: str, text: str) -> None:
        print("Triggering IFTTT webhook...")
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "value1": subject,
            "value2": text
        }

        r = requests.post(self.entry_point, json=data)
        if r.status_code != 200:
            raise Exception(r.status_code, r.text)
        
        print("Triggered!", r.text)
