import smtplib
from email.mime.text import MIMEText
import requests

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
    http://sc.ftqq.com
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

