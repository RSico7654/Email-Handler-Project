from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
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

# Fetch and handle spam emails
def fetch_spam_emails(service):
    print("Fetching spam emails...")
    results = service.users().messages().list(userId='me', labelIds=['SPAM'], maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No spam messages found.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']

        # Extract metadata
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        recipient = next((header['value'] for header in headers if header['name'] == 'To'), None)
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        body = None

        # Decode the email body (if available)
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        # Insert email into database
        insert_query = """
        INSERT INTO emails (sender, recipient, subject, body)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (sender, recipient, subject, body))
        connection.commit()

        # Move the email to the primary inbox
        move_to_inbox(service, message['id'])

    cursor.close()
    connection.close()
    print("Spam emails processed and moved to the inbox.")

# Move an email to the primary inbox
def move_to_inbox(service, message_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': ['INBOX'], 'removeLabelIds': ['SPAM']}
    ).execute()
    print(f"Message {message_id} moved to INBOX")

if __name__ == "__main__":
    try:
        # Authenticate Gmail API
        gmail_service = authenticate_gmail()

        # Fetch and process spam emails
        fetch_spam_emails(gmail_service)

    except Exception as e:
        print(f"An error occurred: {e}")
