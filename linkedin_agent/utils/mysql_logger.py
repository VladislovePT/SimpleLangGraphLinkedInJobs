import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# --- Database Configuration ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Global connection pool object
_connection_pool = None

def init_db():
    """
    Initializes the database connection pool and creates the 'logs' table.
    This is thread-safe and should be called once on application startup.
    """
    global _connection_pool
    if _connection_pool:
        return # Avoid re-initializing

    try:
        print("--- (Logger) Creating MySQL Connection Pool ---")
        pool_config = {
            "pool_name": "logger_pool",
            "pool_size": 5, # The number of connections to keep on hand
            "pool_reset_session": True,
            "host": DB_HOST,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME
        }
        _connection_pool = pooling.MySQLConnectionPool(**pool_config)
        print("--- (Logger) Connection Pool created successfully. ---")

        # Test the connection and initialize the schema
        print("--- (Logger) Initializing database schema... ---")
        with _connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                table_schema = """
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    source VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    details JSON
                )
                """
                cursor.execute(table_schema)
                conn.commit()
        print("--- (Logger) Schema initialized successfully. ---")

    except mysql.connector.Error as e:
        print(f"FATAL: Error during DB pool initialization: {e}")
        _connection_pool = None # Ensure pool is None if setup fails

def log(level: str, source: str, message: str, details: dict = None):
    """
    Inserts a new log entry into the database using a pooled connection.
    This function is thread-safe.
    """
    if not _connection_pool:
        print("--- Fallback Print (Logger not initialized) ---")
        print(f"{datetime.now()} [{level}] {source}: {message}")
        return

    try:
        # The 'with' statements ensure the connection is automatically returned to the pool
        with _connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO logs (timestamp, level, source, message, details)
                VALUES (%s, %s, %s, %s, %s)
                """
                now = datetime.now()
                details_json = json.dumps(details) if details else None
                
                cursor.execute(insert_query, (now, level, source, message, details_json))
                conn.commit()
    except mysql.connector.Error as e:
        print(f"Error writing log to database: {e}")
        print("--- Fallback Print (logging to DB failed) ---")
        print(f"{datetime.now()} [{level}] {source}: {message}")