import smtplib
from email.mime.text import MIMEText
from inspect import cleandoc

import requests
from datetime import datetime

class NotificationHelper:
    """
    Interface for Notification Helper
    """
    def notify(self, subject: str, text: str) -> None:
        """
        Trigger the notification.

        :param subject: The notification subject line
        :param text: The notification body text
        """
        raise NotImplementedError()

class EmailNotification(NotificationHelper):
    """
    Send an email from the student to the student (with provided email address and password)
    """
    def __init__(self, username: str, password: str) -> None:
        # these are unlikely to change
        self.UNIMELB_SMTP_HOST = "smtp.gmail.com"
        self.UNIMELB_SMTP_PORT = 587

        # the script will send email from and to your student email address.
        # if you need to use an app-specific password to get around 2FA on
        # your email account, or other authentication issues, you can set it
        # here as the value of EMAIL_PASSWORD.
        self.EMAIL_ADDRESS  = username + "@student.unimelb.edu.au"
        self.EMAIL_PASSWORD = password

    def notify(self, subject: str, text: str) -> None:
        print("Sending an email to self...")
        print("From/To:", self.EMAIL_ADDRESS)
        print("Subject:", subject)
        print("Message:", '"""', text, '"""', sep="\n")
        
        # make the email object
        msg = MIMEText(text)
        msg['To'] = self.EMAIL_ADDRESS
        msg['From'] = f"WAM Spammer <{self.EMAIL_ADDRESS}>"
        msg['Subject'] = subject

        # log into the unimelb student email SMTP server (gmail) to send it
        s = smtplib.SMTP(self.UNIMELB_SMTP_HOST, self.UNIMELB_SMTP_PORT)
        s.ehlo(); s.starttls()
        s.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
        s.sendmail(self.EMAIL_ADDRESS, [self.EMAIL_ADDRESS], msg.as_string())
        s.quit()
        print("Sent!")


class ServerChanNotification(NotificationHelper):
    """
    Send notification to wechat using ServerChan.
    https://sc.ftqq.com
    """
    def __init__(self) -> None:
        token = input("SCKEY: ")
        self.api = "https://sc.ftqq.com/{}.send".format(token)

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")
        
        data = {
                "text": subject,
                "desp": text
        }
        r = requests.get(self.api, params = data)
        if r.json()["errno"] == 0:
            print("Sent!", r.text)
        else:
            raise Exception(r.text)


class PushBulletNotification(NotificationHelper):
    """
    Send notification using PushBullet.
    https://www.pushbullet.com
    """
    def __init__(self) -> None:
        self.token = input("Pushbullet Access Token: ")

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "type": "note",
            "title": subject,
            "body": text
        }

        r = requests.post("https://api.pushbullet.com/v2/pushes", auth=(self.token, ''), json=data)
        if r.status_code == 200:
            print("Sent!", r.text)
        else:
            raise Exception(r.status_code, r.text)


class TelegramBotNotification(NotificationHelper):
    """
    Send notification using Telegram Bot API.

    Telegram bot can be created with @BotFather (https://t.me/botfather).
    """

    def __init__(self) -> None:
        print(cleandoc("""
        Setup Telegram bot notifications
        ================================

        Please provide your Telegram bot access token. Your token can be 
        obtained from @BotFather (https://t.me/botfather), and should in the 
        following format:

            123456789:AaBbCcDdEeFfGgHhIiJjKkLlMm
        
        If you don't yet have a bot, you can make one with @BotFather.
        """))
        self.token = input("Access token: ")
        print(cleandoc("""

        Please provide your destination of messages. This should be:

            - a numerical ID of a user, group or channel, which can be obtained
              with bots like @GetIDBot (https://t.me/getidbot)
            - Username of a *public group*, e.g. @lyricova
        
        """))
        self.chat = input("Destination: ")

        print(cleandoc("""

        Now you are all set. Please make sure to send at least a message to 
        the bot if you just created one, and ensure that the bot is able to
        deliver message to your destination.
        """))

        self.entry_point = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def notify(self, subject: str, text: str) -> None:
        print("Message:", '"""', text, '"""', sep="\n")

        data = {
            "text": f"<b>{subject}</b>\n\n{text}",
            "chat_id": self.chat,
            "parse_mode": "html",
            "disable_web_page_preview": True
        }

        r = requests.post(self.entry_point, json=data)
        if r.status_code == 200:
            print("Sent!", r.text)
        else:
            raise Exception(r.status_code, r.text)


class IFTTTWebhookNotification(NotificationHelper):
    """
    Send notification using IFTTT WebHook.

    You can obtain your webhook key at https://ifttt.com/maker_webhooks.

    Messages will be sent in "wam-spam" event, with "value1" as the title,
    and "value2" as the body text.
    """

    def __init__(self) -> None:
        print(cleandoc("""
        Setup IFTTT webhook notifications
        ================================

        Please provide your IFTTT webhook key. Your key can be retrieved at
        https://ifttt.com/maker_webhooks., and should in the following format:

            Aa0Bb1Cc2Dd3Ee4Ff5Gg6H

        """))
        self.key = input("Webhook key: ")

        print(cleandoc("""

        Now you are all set. Following messages will be sent with 
        "wam-spam" event, with "value1" as the title, and "value2" as the 
        body text. Any applet setup with the propper event will be triggered
        when an update is available
        """))

        self.entry_point = f"https://maker.ifttt.com/trigger/wam-spam/with/key/{self.key}"

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

class DesktopNotification(NotificationHelper):
    """
    Sends a desktop notification using the notify2 python library (https://pypi.org/project/notify2/)
    """

    def __init__(self) -> None:
        import notify2
        notify2.init("UoM-WAM-Spam")
        self.notification = notify2.Notification
        self.timeout = notify2.EXPIRES_NEVER

    def notify(self, subject: str, text: str) -> None:
        n = self.notification(subject, text)
        n.set_timeout(self.timeout)
        n.show()

class LogFile(NotificationHelper):
    """
    Writes 'notifications' to a local file.
    """

    def __init__(self) -> None:
        self.fp = input("Enter the file path to log WAM changes to: ")

    def notify(self, subject: str, text: str) -> None:
        print("writing notification to log file at: ", self.fp)
        with open(self.fp, 'a+') as f:
            f.write('=' * 20 + '\nTime: ' + datetime.now().strftime('%a, %d %b %Y %H:%M:%S') + '\n' + subject + '\n' + text + '=' * 20 + '\n')
