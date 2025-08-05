"""
This module provides a function that creates a PostgreSQL database,
even if it does not exist
"""

import logging

import asyncpg

from wallet_app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

dbname = settings.DB_NAME
user = settings.DB_USER
password = settings.DB_PASSWORD
host = settings.DB_HOST
port = settings.DB_PORT


async def create_db() -> None:
    """A function that connects to a postgres database
    and checks if a database named `dbname` exists,
    otherwise it creates a new database with that name."""
    conn = await asyncpg.connect(
        database="postgres",
        user=user,
        password=password,
        host=host,
        port=port
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", dbname
        )
        if not exists:
            logging.info("Creating database %s", dbname)
            await conn.execute(f'CREATE DATABASE "{dbname}"')
        else:
            logging.info("Database %s already exists", dbname)
    except asyncpg.PostgresError as e:
        logging.error("Error in create_db function: %s", e)

    finally:
        await conn.close()
