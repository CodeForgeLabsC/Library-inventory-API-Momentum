from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas


def create_book(db: Session, payload: schemas.BookCreate) -> models.Book:
    existing = db.get(models.Book, payload.serial_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book with this serial number already exists.",
        )

    book = models.Book(
        serial_number=payload.serial_number,
        title=payload.title,
        author=payload.author,
        is_borrowed=False,
        borrowed_at=None,
        borrower_card_number=None,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books(db: Session) -> list[models.Book]:
    return db.query(models.Book).order_by(models.Book.serial_number.asc()).all()


def delete_book(db: Session, serial_number: str) -> None:
    book = db.get(models.Book, serial_number)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )
    db.delete(book)
    db.commit()


def update_book_status(
    db: Session,
    serial_number: str,
    payload: schemas.BookStatusUpdate,
) -> models.Book:
    book = db.get(models.Book, serial_number)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    if payload.status == "borrowed":
        if book.is_borrowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book is already borrowed.",
            )
        book.is_borrowed = True
        book.borrowed_at = datetime.now(timezone.utc)
        book.borrower_card_number = payload.borrower_card_number
    else:
        if not book.is_borrowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book is already available.",
            )
        book.is_borrowed = False
        book.borrowed_at = None
        book.borrower_card_number = None

    db.commit()
    db.refresh(book)
    return book
