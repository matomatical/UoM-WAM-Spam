
"""
OAuth/Gmail API-based email notifier

:author: alanung and Matthew Farrugia-Roberts
"""

import base64
import pickle
import os.path

from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


class GmailAPINotifier:
    """Class to send emails using the Gmail API and OAuth 2.0 Protocol.

    To use this class, you must obtain an OAuth 2.0 Client ID from the
    Google API Console (https://console.developers.google.com).
    """

    CLIENT_ID_PATH = 'credentials.json'
    ACCESS_TOKEN_PATH = 'token.pickle'

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, address):
        """
        Initialise a Mailer object. Prompt the user to authenticate and
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

    def notify(self, subject, text):
        msg = MIMEText(text)
        msg['To'] = self.address
        msg['From'] = self.address
        msg['Subject'] = subject
        
        data = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

        self.service.users().messages().send(userId='me', body=data).execute()
        print("Email sent!")
