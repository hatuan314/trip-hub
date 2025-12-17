from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db() -> AsyncIterator[None]:
    yield
