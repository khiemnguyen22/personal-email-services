import os.path
import email
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailService:
    
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # Call the Gmail API
        self.service = build("gmail", "v1", credentials=creds)

    def list_gmail_labels(self):
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for label in labels:
            print(label["name"])
    
    def list_latest_emails(self, query):
        results = self.service.users().messages().list(userId="me", q = query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
        return messages[0]['id']

    def get_message(self, message_id):
        # get a message
        message = self.service.users().messages().get(userId='me', id=message_id, format='raw').execute()

        # Parse the raw message.
        mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(message['raw']))

        print('From: ',mime_msg['from'])
        print('To: ', mime_msg['to'])
        print('Subject: ',mime_msg['subject'])

        print("----------------------------------------------------")
        # Find full message body
        message_main_type = mime_msg.get_content_maintype()
        if message_main_type == 'multipart':
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    print(part.get_payload())
        elif message_main_type == 'text':
            print(mime_msg.get_payload())
        print("----------------------------------------------------")


def main():
    try:
        GmailServiceClient = GmailService()

        # list email labels
        # GmailServiceClient.list_gmail_labels()

        # Get Last email
        last_email_id = GmailServiceClient.list_latest_emails('in:inbox is:unread')
        if last_email_id:
            GmailServiceClient.get_message(last_email_id)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()