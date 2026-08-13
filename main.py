
from fastapi import APIRouter, Depends, HTTPException, status, Query , FastAPI
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Role, Author, Book, UserRoleEnum
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserWithRolesResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    AuthorCreate, AuthorUpdate, AuthorResponse, AuthorWithBooksResponse,
    BookCreate, BookUpdate, BookResponse, BookWithAuthorsResponse,
    LoginRequest, LoginResponse,
    PaginationParams, PaginatedResponse,
    ErrorResponse, SuccessResponse
)

securety = HTTPBearer ()
app = FastAPI()

@app.post("/login/")
def create_user(credential: HTTPAuthorizationCredentials = Depends(securety)):
    print(credential)
    return {}
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """ایجاد کاربر جدید"""
    # بررسی وجود کاربر با همین نام کاربری یا ایمیل
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نام کاربری یا ایمیل قبلاً ثبت شده است"
        )
    # ایجاد کاربر جدید
    new_user = User(
        username=user.username,
        email=user.email,
        password= user.hash_password(user.password),  # در واقع باید هش شود
        first_name=user.first_name,
        last_name=user.last_name
    )