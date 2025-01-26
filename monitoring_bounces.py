import base64
from googleapiclient.errors import HttpError

def send_reply(service, message_id, recipient, reply_body):
    try:
        message = {
            'raw': base64.urlsafe_b64encode(reply_body.encode("utf-8")).decode("utf-8")
        }
        send_response = service.users().messages().send(userId='me', body=message).execute()
        print(f"Replied to message ID: {message_id}")

        # Check if the message was bounced or flagged
        # This part would depend on the feedback you get from email service or Gmail API
        # You can also use the "labelIds" attribute to track spam/junk email labels
        if 'SPAM' in send_response.get('labelIds', []):
            print(f"Message {message_id} was marked as spam.")
        
    except HttpError as error:
        print(f"Failed to send reply: {error}")
