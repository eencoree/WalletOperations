"""
This module describes fixtures for tests
"""

import os

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import create_database, drop_database

# Set test supplement before loading settings
# (settings depends on os.environ['TEST'])
os.environ['TEST'] = '_test'

# Local imports after setting env
from wallet_app.deps import get_db, get_transaction_session
from wallet_app.config import settings


@pytest.fixture(scope='session')
def base_wallets_url() -> str:
    """
    Function returns a base wallet URL.
    """
    return "/api/v1/wallets"


@pytest.fixture(scope='session')
def temp_db() -> str:
    """
    Creates a temporary database for tests.

    Database created by synchronous function 'create_database'
    and deleted by synchronous function 'drop_database'.
    Applies alembic migrations and yields async-compatible DB URL.
    :return: async-compatible database URL.
    """
    database_url = settings.get_db_url().replace(
        'postgresql+asyncpg', 'postgresql'
    )
    create_database(database_url)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")

    yield database_url.replace('postgresql', 'postgresql+asyncpg')
    drop_database(database_url)


@pytest_asyncio.fixture
async def async_client(temp_db: str) -> AsyncClient:
    """
    Creates an asynchronous client.

    Overrides application's dependencies:
    function 'get_db' and 'get_transaction_session'
    for correct asynchronous tests.
    :param temp_db: temporary database.
    :return: asynchronous client.
    """
    from wallet_app.main import app

    engine = create_async_engine(temp_db, poolclass=NullPool)
    test_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with test_session() as session:
            try:
                yield session
            finally:
                await session.close()

    async def override_get_transaction_session():
        async with test_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_transaction_session] = (
        override_get_transaction_session
    )

    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with (AsyncClient(transport=transport, base_url="http://test")
                as client):
        yield client

    app.dependency_overrides.clear()
