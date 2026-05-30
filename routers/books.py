from fastapi import APIRouter, HTTPException, Depends, Query, Request
from database import get_session
from models import BookCreate, BookResponse, BookUpdate, Book
# from auth import verify_api_key
from sqlmodel import Session, select
from typing import Optional
from limiter import limiter
from security import get_current_user

router = APIRouter(prefix="/books", tags=["books"])

# @router.get("", response_model=list[BookResponse])
@router.get("", response_model=list[BookResponse], dependencies=[Depends(get_current_user)])
@limiter.limit("60/minute")
def list_books(
    request: Request,
    session: Session = Depends(get_session), 
    author: Optional[str] = Query(None),
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0)
    ):
    
    query = select(Book)
    if author:
        query = query.where(Book.author == author)
    query = query.offset(offset).limit(limit)
    books = session.exec(query).all()
    return books

# @router.get("/{book_id}", response_model=BookResponse)
@router.get("/{book_id}", response_model=BookResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("60/minute")
def get_book(
    request: Request,
    book_id: int, 
    session: Session = Depends(get_session)
    ):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# @router.post("", response_model=BookResponse, status_code=201, dependencies=[Depends(verify_api_key)])
@router.post("", response_model=BookResponse, status_code=201, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
def create_book(
    request: Request,
    book: BookCreate, 
    session: Session = Depends(get_session)
    ):
    new_book = Book(title=book.title, author=book.author, year=book.year)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book

# @router.put("/{book_id}", response_model=BookResponse, dependencies=[Depends(verify_api_key)])
@router.put("/{book_id}", response_model=BookResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
def update_book(
    request: Request,
    book_id: int, 
    book: BookCreate, 
    session: Session = Depends(get_session)
    ):
    existing_book = session.get(Book, book_id)
    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    existing_book.title = book.title
    existing_book.author = book.author
    existing_book.year = book.year
    session.add(existing_book)    
    session.commit()
    session.refresh(existing_book)

    return existing_book

# @router.delete("/{book_id}", dependencies=[Depends(verify_api_key)])
@router.delete("/{book_id}", dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
def delete_book(
    request: Request,
    book_id: int, 
    session: Session = Depends(get_session)
    ):

    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    session.delete(book)
    session.commit()
    
    return {"message": "Book deleted"}
    

# @router.patch("/{book_id}", response_model=BookResponse, dependencies=[Depends(verify_api_key)])
@router.patch("/{book_id}", response_model=BookResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
def patch_book(
    request: Request,
    book_id: int, 
    book: BookUpdate, 
    session: Session = Depends(get_session)):
    
    existing_book = session.get(Book, book_id)
    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    updates = book.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(existing_book, key, value)
    session.add(existing_book)
    session.commit()
    session.refresh(existing_book)
    
    return existing_book
    