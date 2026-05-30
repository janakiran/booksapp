import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from database import get_session
from models import User

# JWT needs its own secret to sign tokens (seperate from the API key).
# In production, set this as an env var on Render. Falls back for local dev.
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-insecure-secret-do-not-use-in-production-1234567890")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---- Password hashing (bcrypt) ----
def hash_password(plain_password: str)-> str:
    # bcrypt works on bytes; we encode in, decode the hash back to str for storage.
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

# ---- JWT tokens ----

def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}      # 'sub' = subject (who), 'exp' = expiry
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> str | None:
    # Returns the username if the token is valid, else None.
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
) -> User:
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    
    return user