# Library Inventory API

## Project Summary

**Library Inventory API** is a polished FastAPI backend built to manage a library's book catalogue and borrowing workflow. This repository demonstrates production-ready API design with strong validation, database migrations, Docker-based deployment, and end-to-end automated tests.

## Why this project matters

- Clean RESTful API design with clear business rules
- Modern Python stack using FastAPI, SQLAlchemy 2.0, and Pydantic
- Dockerized development environment for fast onboarding
- Comprehensive test coverage for key behaviors
- Database migration support with Alembic

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 ORM
- PostgreSQL
- Pydantic
- Alembic
- Docker + Docker Compose
- Pytest

## Architecture Overview

- `app/main.py` — application entry point with FastAPI and lifecycle startup logic
- `app/database.py` — SQLAlchemy engine, session factory, and dependency injection
- `app/models.py` — declarative Book ORM model with timestamps and borrow state
- `app/schemas.py` — request/response schemas and validation logic
- `app/crud.py` — repository-style operations with business rules and HTTP error handling
- `app/routers/books.py` — REST endpoints for book CRUD and status updates
- `alembic/` — migration configuration and schema versioning
- `tests/test_books.py` — automated tests covering API workflows and validation

## Features

- Create, list, update, and delete books
- Borrow and return books with enforced status transitions
- Validation for serial numbers and borrower card numbers
- Automatic database initialization during startup
- Docker Compose orchestration for API + PostgreSQL
- SQL migration history via Alembic
- Health check endpoint

## Getting started

### Local development with Docker

```bash
docker compose up --build
```

Then open:

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Database migrations

Use Alembic when you want migration-based schema control.

```bash
docker compose exec api alembic upgrade head
```

If the database already exists and the schema was created automatically, initialize the migration state:

```bash
docker compose exec api alembic stamp head
```

Check the current revision:

```bash
docker compose exec api alembic current
```

## API endpoints

- `POST /books` — create a new book
- `GET /books` — retrieve all books
- `PATCH /books/{serial_number}/status` — borrow or return a book
- `DELETE /books/{serial_number}` — delete a book
- `GET /health` — service health check

## Example requests

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

## Business rules enforced

- `serial_number` must be exactly 6 digits
- `borrower_card_number` must be exactly 6 digits when borrowing
- New books are created in an available state
- Cannot borrow a book that is already borrowed
- Cannot return a book that is already available
- Borrowing sets `borrowed_at` to the current UTC timestamp
- Returning clears borrower metadata and sets `is_borrowed` to false

## Notes for reviewers

This project is designed to highlight practical API implementation skills, including:

- schema validation and status-driven workflows
- SQLAlchemy ORM modeling and session management
- Docker-based local development
- test-driven behavior verification
- migration-aware database deployment
