"""This module provides asynchronous session generators for database access"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncTransaction

from wallet_app.database import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous database session generator.

    The session is automatically closed after use."""
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_transaction_session() -> AsyncGenerator[AsyncTransaction, None]:
    """Asynchronous database session generator for transactions.

    Allows you to perform operations within a transaction.
    After the work, a commit is performed if there are no exceptions,
    otherwise, the transaction will be rolled back.
    The session is automatically closed after use."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
