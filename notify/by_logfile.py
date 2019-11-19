"""
local file-based logging notifier

:author: josephsurin
"""

from datetime import datetime


class LogFileNotifier:
    """
    Writes 'notifications' to a local file.
    """
    def __init__(self, filepath: str) -> None:
        print("Configuring Log File Notifier...")
        self.filepath = filepath

    def notify(self, subject: str, text: str) -> None:
        print(f"Appending notification to log file ({self.filepath})...")
        with open(self.filepath, 'a+') as file:
            file.write("====================\n")
            now = datetime.now().strftime('%a, %d %b %Y %H:%M:%S')
            file.write(f"Time: {now}\n")
            file.write(f"{subject}\n")
            file.write(f"{text}\n")
            file.write("====================\n")
        print("Done!")
