
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

CLIENT_ID_PATH = 'gmail-credentials.json'
ACCESS_TOKEN_PATH = 'gmail-token.pickle'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailAPINotifier:
    """Class to send emails using the Gmail API and OAuth 2.0 Protocol.

    To use this class, you must obtain an OAuth 2.0 Client ID from the
    Google API Console (https://console.developers.google.com). See README
    for detailed instructions.
    """

    def __init__(self, address):
        """
        Initialise a GMail notifier object. Prompt the user to authenticate
        and provide mailing permissions if required.
        """
        self.address = address
        self.creds = None
        # if there's an access token from previous authentication, load it
        if os.path.exists(ACCESS_TOKEN_PATH):
            with open(ACCESS_TOKEN_PATH, 'rb') as tokenfile:
                self.creds = pickle.load(tokenfile)

        # if the credentials are invalid or non-existent, prompt to authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_ID_PATH, SCOPES)
                self.creds = flow.run_local_server()
            # save the credentials for the next run
            with open(ACCESS_TOKEN_PATH, 'wb') as tokenfile:
                pickle.dump(self.creds, tokenfile)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def notify(self, subject, text):
        msg = MIMEText(text)
        msg['To'] = self.address
        msg['From'] = self.address
        msg['Subject'] = subject
        
        data = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

        self.service.users().messages().send(userId='me', body=data).execute()
        print("Email sent!")
