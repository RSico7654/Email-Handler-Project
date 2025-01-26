import schedule
import time
import asyncio
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

# Fetch emails with filtering and rules
async def fetch_and_process_emails(service):
    print("Fetching inbox emails...")
    page_token = None
    connection = connect_db()
    cursor = connection.cursor()

    while True:
        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], maxResults=10, pageToken=page_token
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            break

        # Process emails asynchronously
        tasks = [process_email(service, message, cursor) for message in messages]
        await asyncio.gather(*tasks)

        # Get the next page token for pagination
        page_token = results.get('nextPageToken', None)
        if not page_token:
            break

    connection.commit()
    cursor.close()
    connection.close()
    print("Inbox emails processed successfully!")

# Process an individual email
async def process_email(service, message, cursor):
    try:
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

        # Insert email into the database
        insert_query = """
        INSERT INTO emails (sender, recipient, subject, body)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (sender, recipient, subject, body))

        # Apply filters and move emails to appropriate labels
        apply_filters(service, message['id'], subject, body, sender)

    except Exception as e:
        print(f"An error occurred while processing an email: {e}")

# Apply filters and move emails to labels
def apply_filters(service, message_id, subject, body, sender):
    if not subject:
        subject = ""

    # Rule: Move emails with "Invoice" in the subject to the "Invoices" label
    if "invoice" in subject.lower():
        move_to_label(service, message_id, "Label ID: Label_8032219756566567549")
        print(f"Moved email with subject '{subject}' to 'Invoices' label.")

    # Rule: Move emails with "Newsletter" in the sender to the "Newsletters" label
    elif "newsletter" in sender.lower():
        move_to_label(service, message_id, "Label_5916678073306649661")
        print(f"Moved email from sender '{sender}' to 'Newsletters' label.")

    # Rule: Move emails containing "urgent" in the body to "Important"
    elif body and "urgent" in body.lower():
        move_to_label(service, message_id, "Label_6524122743975766562")
        print(f"Moved email with subject '{subject}' to 'Importants' label.")

    # Default Rule: Leave the email in the inbox
    else:
        print(f"No filters applied to email with subject '{subject}'.")

# Move email to a specified label
def move_to_label(service, message_id, label_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
    ).execute()

# Scheduled job to handle emails
def handle_emails():
    service = authenticate_gmail()
    asyncio.run(fetch_and_process_emails(service))

# Schedule the task
def schedule_jobs():
    schedule.every(1).hour.do(handle_emails)  # Run every hour
    print("Scheduler is running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        schedule_jobs()
    except KeyboardInterrupt:
        print("Scheduler stopped.")
