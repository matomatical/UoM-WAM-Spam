import base64
import pickle
import os.path
import smtplib

from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


class Mailer:
    """Class to create email messages following the RFC 2822 standard."""

    @staticmethod
    def create_message(sender, to, subject, body):
        """Create a base-64 encoded email message.

        :param sender: The sender
        :param to: The recipient
        :param subject: Subject line
        :param body: Email body contents
        :return: Object containing the base-64 encoded email message.
        """
        message = MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


class APIMailer(Mailer):
    """Class to send emails using the Gmail API and OAuth 2.0 Protocol.

    To use this class, you must obtain an OAuth 2.0 Client ID from the
    Google API Console (https://console.developers.google.com).
    """

    CLIENT_ID_PATH = 'credentials.json'
    ACCESS_TOKEN_PATH = 'token.pickle'

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self):
        """Initialise a Mailer object. Prompt the user to authenticate and
        provide mailing permissions if required.
        """
        self.creds = None
        # if there's an access token from previous authentication, load it
        if os.path.exists(self.ACCESS_TOKEN_PATH):
            with open(self.ACCESS_TOKEN_PATH, 'rb') as token:
                self.creds = pickle.load(token)

        # if the credentials are invalid or non-existent, prompt to authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_ID_PATH, self.SCOPES)
                self.creds = flow.run_local_server()
            # save the credentials for the next run
            with open(self.ACCESS_TOKEN_PATH, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def send_message(self, message, user_id='me'):
        """Send an email message.

        :param message: Message to be sent
        :param user_id: User's email address (the special value 'me'
        can be used to indicate the authenticated user)
        :return: The sent message
        """
        try:
            message = (self.service.users().messages()
                       .send(userId=user_id, body=message).execute())
            print(f'Email sent! Message Id: {message["id"]}')
            return message
        except HttpError as error:
            print(f'An error occurred: {error}')


class SMTPMailer(Mailer):
    """Class to send emails using SMTP and username/password authentication.

    To use this class, you must enable access by less secure apps in your
    settings (https://myaccount.google.com/u/2/lesssecureapps?pageId=none).

    Warning: This is not a modern method of authentication. Enabling access by
    less secure apps is not recommended.
    """

    def __init__(self, smtp_host, smtp_port, email, password):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def send_message(self, message):
        """Log into the SMTP server and send a message.

        :param message: Message to be sent
        """
        s = smtplib.SMTP(self.smtp_host, self.smtp_port)
        s.ehlo()
        s.starttls()
        s.login(self.email, self.password)
        s.sendmail(self.email, [self.email], message.as_string())
        s.quit()
        print("Email sent!")
