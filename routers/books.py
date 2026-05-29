from fastapi import APIRouter, HTTPException, Depends
from database import get_session
from models import BookCreate, BookResponse, BookUpdate, Book
from auth import verify_api_key
from sqlmodel import Session, select

router = APIRouter(prefix="/books", tags=["books"])

@router.get("", response_model=list[BookResponse])
def list_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
    

@router.post("", response_model=BookResponse, status_code=201, dependencies=[Depends(verify_api_key)])
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    new_book = Book(title=book.title, author=book.author, year=book.year)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book

@router.put("/{book_id}", response_model=BookResponse, dependencies=[Depends(verify_api_key)])
def update_book(book_id: int, book: BookCreate, session: Session = Depends(get_session)):
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

@router.delete("/{book_id}", dependencies=[Depends(verify_api_key)])
def delete_book(book_id: int, session: Session = Depends(get_session)):

    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    session.delete(book)
    session.commit()
    
    return {"message": "Book deleted"}
    

@router.patch("/{book_id}", response_model=BookResponse, dependencies=[Depends(verify_api_key)])
def patch_book(book_id: int, book: BookUpdate, session: Session = Depends(get_session)):
    
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
    