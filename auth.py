# auth.py
from fastapi import Header, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from database import get_db
from models import get_user_by_api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    """Validate if the provided API key exists in the database."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    user = get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return user