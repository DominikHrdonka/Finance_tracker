import sqlite3
import bcrypt

DB_FILE = "finance_tracker.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_user_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def register_user(username: str, password: str) -> bool:
    try:
        hashed = hash_password(password)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

def check_credentials(username: str, password: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return verify_password(password, result[0])
        return False