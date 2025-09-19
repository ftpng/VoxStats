import os
import functools

import pymysql
from pymysql.cursors import Cursor

from dotenv import load_dotenv; load_dotenv()


def _get_database_credentials() -> tuple[str, str, str, str]:
    """
    Load database credentials from environment variables.

    Returns:
        tuple[str, str, str, str]: A tuple containing
            (username, password, database name, endpoint).
    """
    db_username = os.getenv('DBUSER')
    db_password = os.getenv('DBPASS')
    db_name = os.getenv('DBNAME')
    db_endpoint = os.getenv('DBENDPOINT')
    
    return db_username, db_password, db_name, db_endpoint


def db_connect():
    """
    Create a new connection to the database.
    Uses credentials from environment variables.

    Returns:
        pymysql.Connection: A PyMySQL connection object with autocommit enabled.
    """
    db_username, db_password, db_name, db_endpoint = _get_database_credentials()
    conn = pymysql.connect(
        host=db_endpoint,
        port=3306,
        user=db_username,
        password=db_password,
        db=db_name,
        autocommit=True
    )
    return conn


def ensure_cursor(func):
    """
    Decorator to ensure a database cursor is available for a function.

    If a `cursor` argument is provided, it is reused.
    Otherwise, a new connection and cursor are created for the function call.

    Args:
        func (Callable): A function that expects a `cursor` keyword argument.

    Returns:
        Callable: Wrapped function with guaranteed `cursor` available.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor:
            return func(*args, **kwargs)

        with db_connect() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return func(*args, **kwargs)

    return wrapper


def async_ensure_cursor(func):
    """
    Async decorator to ensure a database cursor is available for a coroutine.

    If a `cursor` argument is provided, it is reused.
    Otherwise, a new connection and cursor are created for the coroutine call.

    Args:
        func (Coroutine): An async function that expects a `cursor` keyword argument.

    Returns:
        Coroutine: Wrapped coroutine with guaranteed `cursor` available.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor:
            return await func(*args, **kwargs)

        with db_connect() as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return await func(*args, **kwargs)

    return wrapper