"""
This module creates the FastAPI app with lifecycle management
and includes the router
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from wallet_app.database import engine
from wallet_app.initdb import create_db
from wallet_app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    Lifespan context manager for the FastAPI app.

    Calls 'create_db' function to ensure the database exists,
    then yields control to the app. On shutdown,
    disposes the global database engine.
    """
    await create_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
