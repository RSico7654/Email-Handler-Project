import psycopg2
from dotenv import load_dotenv
import os

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

# Clear the emails table
def clear_email_data():
    connection = connect_db()
    cursor = connection.cursor()

    # SQL query to delete all rows in the 'emails' table
    delete_query = "DELETE FROM emails;"
    cursor.execute(delete_query)
    connection.commit()

    print("All email records have been deleted from the database.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    clear_email_data()
