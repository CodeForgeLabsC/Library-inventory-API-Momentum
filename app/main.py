import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app.database import Base, engine
from app.routers.books import router as books_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    retries = 30
    delay_seconds = 2
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database is ready and tables are created.")
            break
        except OperationalError as exc:
            logger.warning(
                "Database is not ready (attempt %s/%s): %s",
                attempt,
                retries,
                exc,
            )
            if attempt == retries:
                raise
            await asyncio.sleep(delay_seconds)
    yield


app = FastAPI(title="Library Inventory API", lifespan=lifespan)
app.include_router(books_router, prefix="/books", tags=["books"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
