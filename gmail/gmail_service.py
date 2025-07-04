import os.path
import email
import base64
from xhtml2pdf import pisa
import pdfkit
import html2text
import io 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

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
    
    def list_latest_emails(self, query, limit):
        results = self.service.users().messages().list(userId="me", q = query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
        return messages[:limit]

    def get_message(self, message_id):
        # get a message
        message = self.service.users().messages().get(userId='me', id=message_id, format='raw').execute()

        # Parse the raw message.
        mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(message['raw']))

        print('From: ',mime_msg['from'])
        print('To: ', mime_msg['to'])
        print('Subject: ',mime_msg['subject'])

        # Find full message body
        # print("----------------------------------------------------")
        message_main_type = mime_msg.get_content_maintype()
        if message_main_type == 'multipart':
            full_message = ""
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    full_message += part.get_payload(decode=True).decode(part.get_content_charset())
            return mime_msg['subject'], '<pre>' + full_message + '</pre>'
        elif message_main_type == 'text':
            return mime_msg['subject'], '<pre>' + mime_msg.get_payload() + '</pre>'
        # print("----------------------------------------------------")

    def mark_email_as_read(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

        print(f'Mark email {message_id} as read!')
        return message_id

    def forward_email(self, message_id: str, forward_to: str):
        try:
            # Get the original message
            original_message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()

            # Extract original headers and body
            payload = original_message.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            snippet = original_message.get('snippet', '')
            
            # Create the email content
            msg = MIMEMultipart()
            msg['to'] = forward_to
            msg['subject'] = f"Fwd: {subject}"

            body = f"Forwarded message:\nFrom: {from_email}\n\n{snippet}"
            msg.attach(MIMEText(body, 'plain'))

            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            # Send the email
            message = {
                'raw': raw_message
            }
            sent_message = self.service.users().messages().send(userId='me', body=message).execute()

            print(f"Message forwarded to {forward_to}. Message ID: {sent_message['id']}")
            return sent_message

        except Exception as e:
            print(f"An error occurred while forwarding the email: {e}")
            return None
        
    def extract_text_from_message(self, message, txt_path):
        try:
            print('text output: ', html2text.html2text(message))
            with io.open(txt_path, "w", encoding="utf-8") as f:
                f.write(message)
            
            print(f'Text file generated at: {txt_path}')
            return True
        except Exception as e:
            print('error writing to file ', e)
            return False

    def convert_message_to_pdf(self, message, pdf_path):
        # Generate PDF
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(message, dest=pdf_file)
            
        if not pisa_status.err:
            print(f'Email PDF generated at: {pdf_path}')
        return not pisa_status.err
        # try:
        #     with open(pdf_path, "wb") as pdf_file:
        #         pdfkit.from_string(message, pdf_path)
        #     return True
        # except:
        #     return False