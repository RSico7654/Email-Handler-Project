import asyncio
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_batch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="email_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Database connection details
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "email_control")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS")

# Connect to PostgreSQL
def connect_db():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        logging.info("Connected to PostgreSQL database.")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        raise

# Authenticate Gmail API
def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        logging.info("Gmail API authenticated successfully.")
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        logging.error(f"Error authenticating Gmail API: {e}")
        raise

# Fetch emails with pagination and process in batches
async def fetch_and_process_emails(service, batch_size=1000):
    logging.info("Starting to fetch emails...")
    page_token = None
    connection = connect_db()
    cursor = connection.cursor()

    try:
        while True:
            results = service.users().messages().list(
                userId='me', labelIds=['INBOX'], maxResults=500, pageToken=page_token
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                logging.info("No more emails to process.")
                break

            # Process emails concurrently
            tasks = [process_email(service, message) for message in messages]
            email_data = await asyncio.gather(*tasks)

            # Insert emails into the database in batches
            insert_emails_in_batches(cursor, email_data, batch_size)

            # Get the next page token
            page_token = results.get('nextPageToken', None)
            if not page_token:
                break

        connection.commit()
        logging.info("All emails processed successfully.")
    except Exception as e:
        logging.error(f"Error during email fetching and processing: {e}")
    finally:
        cursor.close()
        connection.close()
        logging.info("Database connection closed.")

# Process an individual email
async def process_email(service, message):
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

        logging.info(f"Processed email from: {sender}, subject: {subject}")
        return (sender, recipient, subject, body)
    except Exception as e:
        logging.error(f"Error processing email: {e}")
        return None

# Insert emails into the database in batches
def insert_emails_in_batches(cursor, email_data, batch_size):
    try:
        email_data = [email for email in email_data if email]  # Remove None entries
        query = """
        INSERT INTO emails (sender, recipient, subject, body)
        VALUES (%s, %s, %s, %s)
        """
        for i in range(0, len(email_data), batch_size):
            batch = email_data[i:i+batch_size]
            execute_batch(cursor, query, batch)
            logging.info(f"Inserted {len(batch)} emails into the database.")
    except Exception as e:
        logging.error(f"Error during batch insertion: {e}")

# Scheduled job to handle emails
def handle_emails():
    service = authenticate_gmail()
    asyncio.run(fetch_and_process_emails(service, batch_size=1000))

if __name__ == "__main__":
    try:
        handle_emails()
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}")
