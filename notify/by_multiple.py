"""
Multiple-method notifier

:author: Matthew Farrugia-Roberts
"""

class MultiNotifier:
    def __init__(self, notifiers=None):
        if notifiers is not None:
            self.notifiers = notifiers
        else:
            self.notifiers = []

    def add_notifier(self, notifier):
        self.notifiers.append(notifier)

    def notify(self, subject: str, text: str) -> None:
        print("Triggering all notification methods...")
        problems = []
        nsuccess, nfail = 0, 0
        for notifier in self.notifiers:
            try:
                notifier.notify(subject, text)
                nsuccess += 1
            except Exception as e:
                problems.append((notifier, e))
                nfail += 1
        print(f"{nsuccess} notification methods triggered, {nfail} failed.")
        if problems != []:
            raise Exception("Some notification methods failed.", *problems)
