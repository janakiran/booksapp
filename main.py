from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging
logger = setup_logging()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter

from database import create_db_and_tables
from routers import books, auth

import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up - creating database and tables.")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Register the limiter with the app + the handler that returns 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    reponse = await call_next(request)      # run the actual route
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        reponse.status_code,
        duration_ms
    )
    
    return reponse

app.include_router(books.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Books API"}
