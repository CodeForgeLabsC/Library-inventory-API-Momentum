from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_book_successfully():
    response = client.post(
        "/books",
        json={"serial_number": "123456", "title": "Dune", "author": "Frank Herbert"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["serial_number"] == "123456"
    assert body["is_borrowed"] is False
    assert body["borrowed_at"] is None
    assert body["borrower_card_number"] is None


def test_reject_invalid_serial_number():
    response = client.post(
        "/books",
        json={"serial_number": "ABC123", "title": "Dune", "author": "Frank Herbert"},
    )
    assert response.status_code == 422


def test_reject_duplicate_serial_number():
    payload = {"serial_number": "111111", "title": "Book A", "author": "Author A"}
    first = client.post("/books", json=payload)
    second = client.post("/books", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_list_books():
    client.post(
        "/books",
        json={"serial_number": "111111", "title": "Book A", "author": "Author A"},
    )
    client.post(
        "/books",
        json={"serial_number": "222222", "title": "Book B", "author": "Author B"},
    )

    response = client.get("/books")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["serial_number"] == "111111"
    assert body[1]["serial_number"] == "222222"


def test_borrow_book_successfully():
    client.post(
        "/books",
        json={"serial_number": "333333", "title": "Book C", "author": "Author C"},
    )
    response = client.patch(
        "/books/333333/status",
        json={"status": "borrowed", "borrower_card_number": "654321"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_borrowed"] is True
    assert body["borrowed_at"] is not None
    assert body["borrower_card_number"] == "654321"


def test_reject_borrowing_already_borrowed_book():
    client.post(
        "/books",
        json={"serial_number": "444444", "title": "Book D", "author": "Author D"},
    )
    client.patch(
        "/books/444444/status",
        json={"status": "borrowed", "borrower_card_number": "123123"},
    )
    response = client.patch(
        "/books/444444/status",
        json={"status": "borrowed", "borrower_card_number": "321321"},
    )
    assert response.status_code == 409


def test_return_book_successfully():
    client.post(
        "/books",
        json={"serial_number": "555555", "title": "Book E", "author": "Author E"},
    )
    client.patch(
        "/books/555555/status",
        json={"status": "borrowed", "borrower_card_number": "121212"},
    )
    response = client.patch("/books/555555/status", json={"status": "available"})
    assert response.status_code == 200
    body = response.json()
    assert body["is_borrowed"] is False
    assert body["borrowed_at"] is None
    assert body["borrower_card_number"] is None


def test_reject_returning_already_available_book():
    client.post(
        "/books",
        json={"serial_number": "666666", "title": "Book F", "author": "Author F"},
    )
    response = client.patch("/books/666666/status", json={"status": "available"})
    assert response.status_code == 409


def test_delete_book_successfully():
    client.post(
        "/books",
        json={"serial_number": "777777", "title": "Book G", "author": "Author G"},
    )
    delete_response = client.delete("/books/777777")
    list_response = client.get("/books")
    assert delete_response.status_code == 204
    assert list_response.status_code == 200
    assert list_response.json() == []
