import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User

SECRET_KEY = "my-secret-key-12345"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30

# پسوردهای ویژه
secret_password_admin = "rsehzerfhregwsgeh"
secret_password_editor = "kljj;jhlhbhjkhbkl"


def create_token(user_id: int, type_user: str) -> str:
    """ایجاد توکن JWT"""
    expire = datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.now(),
        "type": type_user
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    """دیکد کردن توکن و برگرداندن payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="امضای توکن نامعتبر است")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توکن نامعتبر است")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="خطا در اعتبارسنجی توکن")


def get_current_user(token: str, db: Session) -> User:
    """دریافت کاربر فعلی از توکن"""
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="شناسه کاربر در توکن یافت نشد")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="کاربر یافت نشد")
    
    return user