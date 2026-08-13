from fastapi import APIRouter, Depends, HTTPException, status, Query
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

router = APIRouter()

# ============================================
# 1. Routes مربوط به Role
# ============================================

@router.post("/roles/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """ایجاد نقش جدید"""
    # بررسی وجود نقش با همین نام
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نقش با این نام قبلاً وجود دارد"
        )
    
    new_role = Role(**role.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.get("/roles/", response_model=List[RoleResponse])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """دریافت لیست همه نقش‌ها"""
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """دریافت نقش با شناسه"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نقش یافت نشد"
        )
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """به‌روزرسانی نقش"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نقش یافت نشد"
        )
    
    update_data = role_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    return role

@router.delete("/roles/{role_id}", response_model=SuccessResponse)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """حذف نقش"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نقش یافت نشد"
        )
    
    db.delete(role)
    db.commit()
    return SuccessResponse(message="نقش با موفقیت حذف شد")

# ============================================
# 2. Routes مربوط به User
# ============================================

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
        password=user.password,  # در واقع باید هش شود
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # اضافه کردن نقش‌ها
    if user.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user.role_ids)).all()
        new_user.roles = roles
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """دریافت لیست کاربران با قابلیت جستجو"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.first_name.contains(search)) | 
            (User.last_name.contains(search)) |
            (User.email.contains(search))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserWithRolesResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """دریافت کاربر با شناسه به همراه نقش‌ها"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """به‌روزرسانی کاربر"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # به‌روزرسانی نقش‌ها
    if 'role_ids' in update_data:
        role_ids = update_data.pop('role_ids')
        if role_ids:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            user.roles = roles
        else:
            user.roles = []
    
    # به‌روزرسانی سایر فیلدها
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", response_model=SuccessResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """حذف کاربر"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    db.delete(user)
    db.commit()
    return SuccessResponse(message="کاربر با موفقیت حذف شد")

# ============================================
# 3. Routes مربوط به Author
# ============================================

@router.post("/authors/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    """ایجاد نویسنده جدید"""
    new_author = Author(**author.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

@router.get("/authors/", response_model=List[AuthorResponse])
def get_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """دریافت لیست نویسندگان با قابلیت جستجو"""
    query = db.query(Author)
    
    if search:
        query = query.filter(
            (Author.first_name.contains(search)) | 
            (Author.last_name.contains(search))
        )
    
    authors = query.offset(skip).limit(limit).all()
    return authors

@router.get("/authors/{author_id}", response_model=AuthorWithBooksResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    """دریافت نویسنده با شناسه به همراه کتاب‌ها"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نویسنده یافت نشد"
        )
    return author

@router.put("/authors/{author_id}", response_model=AuthorResponse)
def update_author(author_id: int, author_update: AuthorUpdate, db: Session = Depends(get_db)):
    """به‌روزرسانی نویسنده"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نویسنده یافت نشد"
        )
    
    update_data = author_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(author, key, value)
    
    db.commit()
    db.refresh(author)
    return author

@router.delete("/authors/{author_id}", response_model=SuccessResponse)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    """حذف نویسنده"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نویسنده یافت نشد"
        )
    
    db.delete(author)
    db.commit()
    return SuccessResponse(message="نویسنده با موفقیت حذف شد")

# ============================================
# 4. Routes مربوط به Book
# ============================================

@router.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """ایجاد کتاب جدید"""
    new_book = Book(
        title=book.title,
        publisher=book.publisher,
        category=book.category,
        description=book.description,
        quantity=book.quantity
    )
    
    # اضافه کردن نویسندگان
    if book.author_ids:
        authors = db.query(Author).filter(Author.id.in_(book.author_ids)).all()
        new_book.authors = authors
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@router.get("/books/", response_model=List[BookResponse])
def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """دریافت لیست کتاب‌ها با فیلترهای مختلف"""
    query = db.query(Book)
    
    if category:
        query = query.filter(Book.category == category)
    
    if search:
        query = query.filter(
            (Book.title.contains(search)) | 
            (Book.publisher.contains(search)) |
            (Book.description.contains(search))
        )
    
    if min_quantity is not None:
        query = query.filter(Book.quantity >= min_quantity)
    
    if max_quantity is not None:
        query = query.filter(Book.quantity <= max_quantity)
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/books/{book_id}", response_model=BookWithAuthorsResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """دریافت کتاب با شناسه به همراه نویسندگان"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کتاب یافت نشد"
        )
    return book

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    """به‌روزرسانی کتاب"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کتاب یافت نشد"
        )
    
    update_data = book_update.model_dump(exclude_unset=True)
    
    # به‌روزرسانی نویسندگان
    if 'author_ids' in update_data:
        author_ids = update_data.pop('author_ids')
        if author_ids:
            authors = db.query(Author).filter(Author.id.in_(author_ids)).all()
            book.authors = authors
        else:
            book.authors = []
    
    # به‌روزرسانی سایر فیلدها
    for key, value in update_data.items():
        setattr(book, key, value)
    
    db.commit()
    db.refresh(book)
    return book

@router.delete("/books/{book_id}", response_model=SuccessResponse)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """حذف کتاب"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کتاب یافت نشد"
        )
    
    db.delete(book)
    db.commit()
    return SuccessResponse(message="کتاب با موفقیت حذف شد")

# ============================================
# 5. Routes مربوط به جستجو و گزارشات
# ============================================

@router.get("/books/by-author/{author_id}", response_model=List[BookResponse])
def get_books_by_author(author_id: int, db: Session = Depends(get_db)):
    """دریافت کتاب‌های یک نویسنده خاص"""
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نویسنده یافت نشد"
        )
    return author.books

@router.get("/authors/by-book/{book_id}", response_model=List[AuthorResponse])
def get_authors_by_book(book_id: int, db: Session = Depends(get_db)):
    """دریافت نویسندگان یک کتاب خاص"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کتاب یافت نشد"
        )
    return book.authors

@router.get("/users/by-role/{role_name}", response_model=List[UserResponse])
def get_users_by_role(role_name: str, db: Session = Depends(get_db)):
    """دریافت کاربران با نقش خاص"""
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نقش یافت نشد"
        )
    return role.users

# ============================================
# 6. Routes آماری
# ============================================

@router.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    """دریافت آمار کلی سیستم"""
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    total_authors = db.query(Author).count()
    total_roles = db.query(Role).count()
    
    # کتاب‌های با موجودی کم
    low_stock_books = db.query(Book).filter(Book.quantity <= 5).count()