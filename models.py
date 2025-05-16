from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import secrets
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def create_user(db, username: str, email: str):
    """Create a new user with a unique API key."""
    api_key = generate_api_key()
    user = User(username=username, email=email, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_api_key(db, api_key: str):
    """Get user by their API key."""
    return db.query(User).filter(User.api_key == api_key).first() 