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

# Create indexes for the frequently queried columns
def create_indexes():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Creating indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender ON emails (sender);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject ON emails (subject);")
        connection.commit()

        print("Indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_indexes()
