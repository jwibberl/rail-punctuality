import sys
import types

# Allow collection even when the PostgreSQL driver is not installed.
# No test makes a real database connection.
try:
    import psycopg2
except ImportError:
    sys.modules['psycopg2'] = types.SimpleNamespace(connect=None)

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def conn():
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value = cursor
    cursor.__enter__.return_value = cursor
    return connection


@pytest.fixture
def cur(conn):
    return conn.cursor.return_value
