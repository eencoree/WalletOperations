"""
This module creates an asynchronous engine and asynchronous session,
as well as a declarative database for models
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from wallet_app.config import settings

DATABASE_URL = settings.get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
