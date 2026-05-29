from fastapi import Header, HTTPException
import os

API_KEY = os.environ.get("BOOKS_API_KEY", "dev-only-key")

def verify_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
