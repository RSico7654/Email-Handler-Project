from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Authenticate Gmail API
def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

# List all Gmail labels
def list_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    for label in labels:
        print(f"Label Name: {label['name']}, Label ID: {label['id']}")

if __name__ == "__main__":
    try:
        # Authenticate Gmail API
        gmail_service = authenticate_gmail()

        # List and print Gmail labels
        list_labels(gmail_service)

    except Exception as e:
        print(f"An error occurred: {e}")
