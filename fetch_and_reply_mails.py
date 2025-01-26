from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email import message_from_bytes
from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables
load_dotenv()

# Database connection details
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "email_control")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS")

# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# Authenticate Gmail API
def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

# Fetch and store emails in the database
def fetch_emails(service):
    # Fetch the first 10 emails
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']

        # Extract required fields
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        recipient = next((header['value'] for header in headers if header['name'] == 'To'), None)
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        body = None

        # Decode the email body (if available)
        if 'parts' in payload['body']:
            for part in payload['body']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        # Insert into database
        insert_query = """
        INSERT INTO emails (sender, recipient, subject, body)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (sender, recipient, subject, body))
        connection.commit()

        # Send an automated reply
        if sender and subject:
            reply_body = f"Hello,\n\nThis is an automated reply to your email with the subject: '{subject}'.\n\nThank you!"
            send_reply(service, message['id'], sender, reply_body)

    cursor.close()
    connection.close()
    print("Emails fetched and stored in the database!")

# Send an automated reply
def send_reply(service, message_id, recipient, reply_body):
    # Create the reply email
    message = f"To: {recipient}\r\nSubject: Re: Your email\r\n\r\n{reply_body}"
    encoded_message = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")

    reply = {
        'raw': encoded_message
    }
    service.users().messages().send(userId='me', body=reply).execute()
    print(f"Replied to {recipient} regarding message ID: {message_id}")

if __name__ == "__main__":
    try:
        # Authenticate and create Gmail API service
        gmail_service = authenticate_gmail()

        # Fetch emails and send replies
        fetch_emails(gmail_service)

    except Exception as e:
        print(f"An error occurred: {e}")
