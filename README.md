# Email Handler Project

## Overview
This project is a scalable Python-based email handling system that integrates with the Gmail API. It efficiently handles large volumes of emails (e.g., 100,000+), fetches and processes emails from the Gmail inbox, applies filters and rules, replies to emails, and stores email metadata in a PostgreSQL database.

### Key Features
- **Fetch Emails**: Fetch emails from Gmail Inbox using the Gmail API.
- **Process Emails**: Process emails in batches using pagination for scalability.
- **Reply to Emails**: Automatically send replies to emails based on predefined criteria.
- **Apply Filters**: Move emails to specific Gmail labels (e.g., `Invoices`, `Newsletters`, `Important`) based on subject, body, or sender.
- **Store Metadata**: Store email metadata (sender, recipient, subject, body) in a PostgreSQL database.
- **Logging**: Automatically log all activities and errors for monitoring and debugging.
- **Scalability**: Designed to handle a large number of emails efficiently.

---

## Prerequisites
Before running the project, ensure you have the following installed:
- **Python 3.9 or higher**
- **PostgreSQL (Version 16 or higher recommended)**
- **Gmail API credentials** (`credentials.json` file)

### Python Dependencies
The following Python libraries are required:
- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`
- `psycopg2`
- `python-dotenv`

---

## Setup Instructions

### 1. Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/RSico7654/Email-Handler-Project.git
cd Email-Handler-Project
```
### 2. Setup The Virtual Environment
Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Configure Gmail API
- Go to the `Google Cloud Console`.
- Enable the `Gmail API` for your project.
- Create `OAuth 2.0 credentials` and download the `credentials.json` file.
- Place the `credentials.json` file in the project directory.

### 4. Configure Environment Variables

Create a `.env` file in the project root and add your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_NAME=email_control
DB_USER=postgres
DB_PASS=your_password
```
### 5. Set Up PostgreSQL Database
- Create the `email_control` database in PostgreSQL.
- Create the  `emails ` table.
- Add indexes for optimized querying.
### 6. Acknowledgements

- [Google Gmail API Documentation](https://developers.google.com/gmail/api)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Conclusion

Thank you for using the Email Handler Project. This system integrates Gmail API and PostgreSQL to automate email handling efficiently. Feel free to contribute or customize it according to your needs!
