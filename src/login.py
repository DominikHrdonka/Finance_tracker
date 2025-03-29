import json

USER_FILE = "users.json"

def load_users():
    """
    Loads users from the JSON file.

    Returns:
        dict: A dictionary of users and their passwords.
    """
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    """
    Saves users to the JSON file.

    Args:
        users (dict): Dictionary containing username-password pairs.
    """
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)