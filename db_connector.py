import mysql.connector  # type: ignore
from dotenv import load_dotenv
import os

load_dotenv()
def conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="aravindh"
    )

def create_table():
    mydb = conn()
    cursor = mydb.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        )
    """)
    
    cursor.close()
    mydb.close()

def insert_user(name, email):
    mydb = conn()
    cursor = mydb.cursor()
    
    sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
    cursor.execute(sql, (name, email))
    
    mydb.commit()
    
    cursor.close()
    mydb.close()
    
    return cursor.rowcount

def get_users():
    mydb = conn()
    cursor = mydb.cursor()
    
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    
    cursor.close()
    mydb.close()
    
    return result