from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    return AuthService.create_user(db=db, user=user)


@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Login a user and return access token."""
    result = AuthService.login_user(db=db, user_login=user_login)
    user_data = User.model_validate(result["user"])
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": user_data
    }


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Refresh the access token."""
    from app.utils.security import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
