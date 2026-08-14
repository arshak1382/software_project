from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from auth_user import decode_token, create_token, secret_password_admin, secret_password_editor
from database import engine, Base, get_db  
import models  
from models import User, UserRoleEnum, Role
from schemas import (
    UserCreate,
    UserResponse,
    Userlogin
)

print("🔄 creating database ...")
Base.metadata.create_all(bind=engine)
print("✅ database created")

app = FastAPI(
    title="سامانه مدیریت کتابخانه",
    description="API برای مدیریت کتابخانه، کاربران و نقش‌ها",
    version="1.0.0"
)

security = HTTPBearer()  

VIOWER = "VIOWER"
EDITOR = "EDITOR"
ADMIN = "ADMIN"


# ============================================
# لاگین کاربر
# ============================================
@app.post("/login/")
def login_user(response: Userlogin, db: Session = Depends(get_db)):
    # پیدا کردن کاربر
    user_obj = db.query(User).filter(User.username == response.username).first()
    
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if not user_obj.verify_password(response.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if response.password == secret_password_admin:
        type_user = ADMIN
    elif response.password == secret_password_editor:
        type_user = EDITOR
    else:
        type_user = VIOWER
    
    # ایجاد توکن با type_user
    access_token = create_token(user_obj.id, type_user)
    return {"access_token": access_token, "token_type": "bearer"}


# ============================================
# ایجاد کاربر جدید
# ============================================
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نام کاربری یا ایمیل قبلاً ثبت شده است"
        )
    
    if user.password == secret_password_admin:
        role_enum = UserRoleEnum.ADMIN
    elif user.password == secret_password_editor:
        role_enum = UserRoleEnum.EDITOR
    else:
        role_enum = UserRoleEnum.VIOWER
    

    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    new_user.set_password(user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    role = db.query(Role).filter(Role.Role_of_user == role_enum).first()
    
    if not role:
        role = Role(Role_of_user=role_enum)
        db.add(role)
        db.commit()
        db.refresh(role)
    
    new_user.roles.append(role)
    
    db.commit()
    db.refresh(new_user)
    
    return new_user



# # ============================================
# # 3. دریافت لیست کاربران (برای تست)
# # ============================================
# @app.get("/users/", response_model=list[UserResponse])
# def get_users(
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db)
# ):
#     """
#     ✅ دریافت لیست کاربران با صفحه‌بندی
#     """
#     users = db.query(User).offset(skip).limit(limit).all()
#     return users

# # ============================================
# # 4. دریافت یک کاربر با ID
# # ============================================
# @app.get("/users/{user_id}", response_model=UserResponse)
# def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
#     """
#     ✅ دریافت اطلاعات یک کاربر با شناسه
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"❌ کاربر با شناسه {user_id} یافت نشد"
#         )
#     return user

# # ============================================
# # 5. به‌روزرسانی کاربر
# # ============================================
# @app.put("/users/{user_id}", response_model=UserResponse)
# def update_user(
#     user_id: int,
#     user_update: UserCreate,  # می‌توانید از UserUpdate استفاده کنید
#     db: Session = Depends(get_db)
# ):
#     """
#     ✅ به‌روزرسانی اطلاعات کاربر
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"❌ کاربر با شناسه {user_id} یافت نشد"
#         )
    
#     # به‌روزرسانی فیلدها
#     user.username = user_update.username
#     user.email = user_update.email
#     user.first_name = user_update.first_name
#     user.last_name = user_update.last_name
    
#     # اگر پسورد جدید داده شده، آن را هش کن
#     if user_update.password:
#         user.set_password(user_update.password)
    
#     db.commit()
#     db.refresh(user)
    
#     print(f"✅ کاربر با ID {user_id} به‌روزرسانی شد")
#     return user

# # ============================================
# # 6. حذف کاربر
# # ============================================
# @app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     """
#     ✅ حذف کاربر از دیتابیس
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"❌ کاربر با شناسه {user_id} یافت نشد"
#         )
    
#     db.delete(user)
#     db.commit()
    
#     print(f"🗑️ کاربر با ID {user_id} حذف شد")
#     return None  # 204 No Content

# # ============================================
# # 7. اندپوینت سلامت (Health Check)
# # ============================================
# @app.get("/health")
# def health_check():
#     """
#     ✅ بررسی وضعیت سرویس
#     """
#     return {
#         "status": "healthy",
#         "message": "✅ سامانه کتابخانه با موفقیت اجرا می‌شود",
#         "timestamp": "2026-08-13"
#     }

# # ============================================
# # اجرای برنامه (برای دیباگ)
# # ============================================
# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 در حال اجرای سامانه کتابخانه...")
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

