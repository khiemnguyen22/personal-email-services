from googleapiclient.errors import HttpError

from gmail_service import GmailService

def main():
    try:
        GmailServiceClient = GmailService()

        # list email labels
        # GmailServiceClient.list_gmail_labels()

        # Get Last email
        last_emails = GmailServiceClient.list_latest_emails('in:inbox is:unread', 10)
        last_email_id = last_emails[0]['id']
        if last_email_id:
            subject, message = GmailServiceClient.get_message(last_email_id)
            message = GmailServiceClient.forward_email(last_email_id, 'knguyen23in2024@gmail.com')
            output_file = 'test_file'
            pdfConvertStatus = GmailServiceClient.convert_message_to_pdf(message, f'./{output_file}.pdf')
            
            txtExtractStatus = GmailServiceClient.extract_text_from_message(message, f'./{output_file}.txt')
            
            if txtExtractStatus or pdfConvertStatus:
                GmailServiceClient.mark_email_as_read(last_email_id)


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()