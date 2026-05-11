from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookBase(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)


class BookCreate(BookBase):
    serial_number: str = Field(pattern=r"^\d{6}$")


class BookStatusUpdate(BaseModel):
    status: Literal["borrowed", "available"]
    borrower_card_number: str | None = Field(default=None, pattern=r"^\d{6}$")

    @model_validator(mode="after")
    def validate_borrower_card_number(self) -> "BookStatusUpdate":
        if self.status == "borrowed" and self.borrower_card_number is None:
            raise ValueError("borrower_card_number is required when borrowing a book.")
        if self.status == "available" and self.borrower_card_number is not None:
            raise ValueError(
                "borrower_card_number must be null when returning a book."
            )
        return self


class BookResponse(BookBase):
    serial_number: str
    is_borrowed: bool
    borrowed_at: datetime | None
    borrower_card_number: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
