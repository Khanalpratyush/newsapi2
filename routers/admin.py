from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from datetime import datetime
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from middleware.admin_auth import verify_admin

router = APIRouter()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

@router.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Render the admin panel HTML page."""
    await verify_admin(credentials)
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/users", response_model=list[UserResponse])
async def get_users(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all users."""
    await verify_admin(credentials)
    users = db.query(User).all()
    return users

@router.post("/users", response_model=UserResponse)
async def create_new_user(
    user: UserCreate,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new user with API key."""
    await verify_admin(credentials)
    # Check if username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    new_user = User(
        username=user.username,
        email=user.email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    await verify_admin(credentials)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/logout")
async def logout():
    """Handle logout request."""
    # Return 401 to force browser to clear credentials
    raise HTTPException(
        status_code=401,
        detail="Logged out successfully",
        headers={"WWW-Authenticate": "Basic"}
    ) 