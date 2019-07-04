"""
notify2-based desktop alert notifier

:author: josephsurin
"""

import notify2

class DesktopNotifier:
    """
    Sends a desktop notification using the notify2 python library
    https://pypi.org/project/notify2/
    """
    def __init__(self) -> None:
        notify2.init("UoM-WAM-Spam")
        self.notification = notify2.Notification
        self.timeout = notify2.EXPIRES_NEVER

    def notify(self, subject: str, text: str) -> None:
        n = self.notification(subject, text)
        n.set_timeout(self.timeout)
        n.show()
