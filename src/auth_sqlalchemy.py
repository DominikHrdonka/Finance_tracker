from sqlalchemy.exc import IntegrityError
from db_models import Session, User
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def register_user(username: str, password: str) -> bool:
    """
    Attempts to register a new user. Returns True if successful, False if user exists.
    """
    session = Session()
    hashed = hash_password(password)
    new_user = User(username=username, password=hashed)
    try:
        session.add(new_user)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()

def check_credentials(username: str, password: str) -> bool:
    """
    Checks if the given credentials match a user in the database.
    """
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password):
            return True
        return False
    finally:
        session.close()