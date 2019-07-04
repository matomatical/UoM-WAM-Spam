"""
IFTTT Webbhook-based notifier

:author: blueset
"""

from inspect import cleandoc

import requests

def setup():
    print(cleandoc("""
    Setup IFTTT webhook notifications
    ================================

    Please provide your IFTTT webhook key. Your key can be retrieved at
    https://ifttt.com/maker_webhooks., and should in the following format:

        Aa0Bb1Cc2Dd3Ee4Ff5Gg6H

    """))
    key = input("Webhook key: ")

    print(cleandoc("""

    Now you are all set. Following messages will be sent with 
    "wam-spam" event, with "value1" as the title, and "value2" as the 
    body text. Any applet setup with the propper event will be triggered
    when an update is available
    """))

    return (key, )

class IFTTTWebhookNotifier:
    """
    Send notification using IFTTT WebHook.

    You can obtain your webhook key at https://ifttt.com/maker_webhooks.

    Messages will be sent in "wam-spam" event, with "value1" as the title,
    and "value2" as the body text.
    """

    def __init__(self, key) -> None:
        self.entry_point = f"https://maker.ifttt.com/trigger/wam-spam/with/key/{key}"

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "value1": subject,
            "value2": text
        }

        r = requests.post(self.entry_point, json=data)
        if r.status_code == 200:
            print("Triggered!", r.text)
        else:
            raise Exception(r.status_code, r.text)
