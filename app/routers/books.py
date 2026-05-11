from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post("", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, payload)


@router.get("", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return crud.list_books(db)


@router.patch(
    "/{serial_number}/status",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_200_OK,
)
def update_book_status(
    serial_number: str,
    payload: schemas.BookStatusUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_book_status(db, serial_number, payload)


@router.delete("/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(serial_number: str, db: Session = Depends(get_db)):
    crud.delete_book(db, serial_number)
