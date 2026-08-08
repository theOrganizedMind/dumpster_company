import os
import logging
from dotenv import load_dotenv
import psycopg2

load_dotenv()

LOGGER = logging.getLogger(__name__)
SAFE_DB_ERROR_MESSAGE = (
    "The database request could not be completed. Verify your local PostgreSQL setup and try again."
)

HOST = os.getenv("POSTGRESQL_HOST")
PORT = os.getenv("POSTGRESQL_PORT")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("POSTGRESQL_USER")
PASSWORD = os.getenv("POSTGRESQL_PASSWORD")


class DatabaseOperationError(RuntimeError):
    """Raised when a database operation fails with a user-safe message."""


def get_db_connection():
    """Create and return a PostgreSQL connection using environment settings."""
    try:
        return psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
        )
    except psycopg2.Error:
        LOGGER.exception("Failed to connect to PostgreSQL.")
        raise DatabaseOperationError(SAFE_DB_ERROR_MESSAGE) from None


def fetch_all(query, params=None, include_columns=False):
    """Execute a query and return rows, optionally including column names."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                if include_columns:
                    columns = [desc[0] for desc in cur.description]
                    return rows, columns
                return rows
    except DatabaseOperationError:
        raise
    except psycopg2.Error:
        LOGGER.exception("PostgreSQL query execution failed.")
        raise DatabaseOperationError(SAFE_DB_ERROR_MESSAGE) from None
