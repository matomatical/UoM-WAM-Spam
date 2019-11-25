"""
SMTP-based Gmail notifier

:author: Matthew Farrugia-Roberts
"""

import getpass
import smtplib
from email.mime.text import MIMEText


GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


class SMTPGmailNotifier:
    def __init__(self, address, password, smtp_host=GMAIL_SMTP_HOST,
                    smtp_port=GMAIL_SMTP_PORT, debug=False):
        """
        :param address: The email address to use (as all three of SMTP login 
                        username, email sender, and email recipient).
        :param password: The password to use for SMTP server login.
        :param smtp_host: Name of the SMTP server.
        :param smtp_port: Port of the SMTP server.
        :param debug: Set True to inhibit sending actual messages
        """
        print("Configuring SMTP Gmail Notifier...")
        self.address = address
        self.password = password
        self.host = smtp_host
        self.port = smtp_port
        self.debug = debug

    def notify(self, subject: str, text: str) -> None:
        """
        Send a self-email.

        :param subject: The email subject line.
        :param text: The email body text.
        """
        print("Sending an email to self...")
        print("From/To:", self.address)
        print("Subject:", subject)
        print("Message:", '"""', text, '"""', sep="\n")
        
        # make the email object
        msg = MIMEText(text)
        msg['To'] = self.address
        msg['From'] = self.address
        msg['Subject'] = subject

        # break early if in debug mode
        if self.debug:
            print("(Debug mode. Not sending)")
            return

        # log into the SMTP server to send it
        s = smtplib.SMTP(self.host, self.port)
        s.ehlo(); s.starttls()
        s.login(self.address, self.password)
        s.sendmail(self.address, [self.address], msg.as_string())
        s.quit()
        print("Sent!")
