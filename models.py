from pydantic import BaseModel, Field, field_validator
from typing import Optional
from sqlmodel import SQLModel, Field as SQLField

class Book(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    title: str
    author: str
    year: int

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int

    @field_validator("year")
    @classmethod
    def check_year(cls, value):
        if value < 1450 or value > 2026:
            raise ValueError("Year must be between 1450 and 2026.")
        return value
    
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int

class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    year: Optional[int] = None