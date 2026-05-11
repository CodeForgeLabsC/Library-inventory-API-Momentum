# Library Inventory API

Recruitment-quality FastAPI backend for managing library book inventory.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 style ORM
- Pydantic validation
- Docker + Docker Compose
- Pytest

## Project Structure

```text
app/
  main.py
  database.py
  models.py
  schemas.py
  crud.py
  routers/
    __init__.py
    books.py
alembic/
  env.py
  script.py.mako
  versions/
    20260510_0001_create_books_table.py
alembic.ini
tests/
  test_books.py
Dockerfile
docker-compose.yml
requirements.txt
README.md
.gitignore
```

## Run With Docker

```bash
docker compose up --build
```

API endpoints:

- API root docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

## Run Tests

Create/activate a virtualenv, install dependencies, then run tests:

```bash
pip install -r requirements.txt
pytest
```

## Optional: Database Migrations (Alembic)

This project keeps automatic table creation on startup for local simplicity, and also includes Alembic for migration-based workflows.

For a fresh database, run migrations in Docker:

```bash
docker compose exec api alembic upgrade head
```

If tables already exist (created by app startup), baseline the DB first:

```bash
docker compose exec api alembic stamp head
```

Check current migration version:

```bash
docker compose exec api alembic current
```

## API Overview

- `POST /books` - add new book
- `GET /books` - list all books
- `PATCH /books/{serial_number}/status` - borrow/return book
- `DELETE /books/{serial_number}` - delete book
- `GET /health` - health check

## Example cURL Commands

Create a book:

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "123456",
    "title": "The Pragmatic Programmer",
    "author": "Andrew Hunt"
  }'
```

List books:

```bash
curl http://localhost:8000/books
```

Borrow a book:

```bash
curl -X PATCH http://localhost:8000/books/123456/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "borrowed",
    "borrower_card_number": "654321"
  }'
```

Return a book:

```bash
curl -X PATCH http://localhost:8000/books/123456/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "available"
  }'
```

Delete a book:

```bash
curl -X DELETE http://localhost:8000/books/123456
```

## Business Rules Implemented

- `serial_number` must be unique and match `^\d{6}$`
- `borrower_card_number` must match `^\d{6}$` when provided
- new books are available by default
- cannot borrow an already borrowed book
- cannot return an already available book
- borrowing sets:
  - `is_borrowed = true`
  - `borrowed_at = current UTC datetime`
  - `borrower_card_number = provided card number`
- returning sets:
  - `is_borrowed = false`
  - `borrowed_at = null`
  - `borrower_card_number = null`
- HTTP errors:
  - `404` for missing books
  - `409` for business conflicts (duplicate serial, invalid state transition)
  - `422` for validation errors
