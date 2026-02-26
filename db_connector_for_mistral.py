import mysql.connector
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def conn():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database="aravindh"
        )
    # CHANGED: Be specific about the connection error
    except mysql.connector.Error as e:
        print(f"🚨 DB CONNECTION FAILED: {e}", file=sys.stderr)
        raise e

def create_table(table_name="users"):
    if not table_name.isalnum():
        raise ValueError("Table name must be alphanumeric (letters/numbers only).")

    mydb = conn()
    cursor = mydb.cursor()
    try:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE
            )
        """
        cursor.execute(sql)
        mydb.commit()
        print(f"✅ DB LOG: Table '{table_name}' ready.", file=sys.stderr)
    # CHANGED: Catch only database-related errors
    except mysql.connector.Error as e:
        print(f"🚨 DB ERROR: {e}", file=sys.stderr)
        raise e
    finally:
        cursor.close()
        mydb.close()

def insert_user(name, email):
    mydb = conn()
    cursor = mydb.cursor()
    rowcount = 0
    try:
        sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(sql, (name, email))
        mydb.commit()
        rowcount = cursor.rowcount
        print(f"✅ DB LOG: Inserted {rowcount} row(s).", file=sys.stderr)
    # CHANGED: Catch only database-related errors
    except mysql.connector.Error as e:
        print(f"🚨 DB ERROR: {e}", file=sys.stderr)
    finally:
        cursor.close()
        mydb.close()
    return rowcount

def get_users():
    mydb = conn()
    cursor = mydb.cursor(dictionary=True)
    result = []
    try:
        cursor.execute("SELECT id, name, email FROM users")
        result = cursor.fetchall()
        print(f"✅ DB LOG: Fetched {len(result)} user(s).", file=sys.stderr)
    # CHANGED: Catch only database-related errors
    except mysql.connector.Error as e:
        print(f"🚨 DB ERROR: {e}", file=sys.stderr)
    finally:
        cursor.close()
        mydb.close()
    return result