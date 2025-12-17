"""Common FastAPI dependencies for the destination service."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_db() -> AsyncIterator[None]:
    # TODO: wire up real database session
    yield
