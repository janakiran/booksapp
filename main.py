from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import create_db_and_tables
from routers import books

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Books API"}
