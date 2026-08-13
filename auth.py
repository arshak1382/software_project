from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

import jwt
from jwt.exceptions import DecodeError , InvalidSignatureError
from datetime import datetime, timedelta

from database import engine, Base, get_db  
import models  
from models import User, UserRoleEnum
from schemas import (
    UserCreate,
    UserResponse,
   
)

app = FastAPI()
security = HTTPBearer()  


@app.post("/login/")
def login_user(credentials: HTTPAuthorizationCredentials = Depends(security) , 
               db : Session = Depends(get_db)):

    return {
    }


SECRET_KEY = "my-secret-key-12345"  
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30  
##### دیکد کردن 
def decode_user(credentials: HTTPAuthorizationCredentials = Depends(security) , 
               db : Session = Depends(get_db)):
    token = credentials.credentials

    try:

        decode_obj = jwt.decode(token ,SECRET_KEY, algorithm=ALGORITHM)
        
        if not decode_obj.get("username" , None) :
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
        
        if datetime.now() > datetime.fromtimestamp(decode_obj.get("exp")):
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
        

    except InvalidSignatureError :
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    except DecodeError :
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

### انکد کردن
def create_token(username: str) -> str:

    expire = datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    
    
    payload = {
        "username": username,  
        "exp": expire,    
        "iat": datetime.now()  
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token