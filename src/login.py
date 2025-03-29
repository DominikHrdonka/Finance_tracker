import json
import bcrypt

USER_FILE = "users.json"

def hash_password(password: str) -> str:
    """Hashes a password with a random salt using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def load_users() -> dict:
    """
    Loads users from the JSON file.

    Returns:
        dict: A dictionary of users with hashed passwords.
    """
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users: dict):
    """
    Saves users to the JSON file.

    Args:
        users (dict): Dictionary containing username → hashed_password pairs.
    """
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)