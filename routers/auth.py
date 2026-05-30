from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, UserCreate, UserResponse, Token
from security import hash_password, verify_password, create_access_token, get_current_user
import logging
logger = logging.getLogger("booksapp")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, session: Session = Depends(get_session)):
    # Reject if username already taken
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered.")
    
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),   #store the HASH, never plaintext
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(user: UserCreate, session: Session = Depends(get_session)):
    # Find the user
    db_user = session.exec(select(User).where(User.username == user.username)).first()

    # Check user exists AND password matches - same error for the both/
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        logger.warning("Failed login attempt for username: %s", user.username)
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    logger.info("User logged in: %s", user.username)
    #Credentials good -> issue a token
    token = create_access_token(db_user.username)
    return Token(access_token=token)

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user