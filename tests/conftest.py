"""Pytest configuration and fixtures for testing."""

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.flask_app.create_app import app as flask_app

# Import routes to register them with the app
from src.flask_app.routes import admin_routers, api_routes, routers


@pytest.fixture
def app() -> Flask:
    """Create and configure a Flask app instance for testing."""
    flask_app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
            "SECRET_KEY": "test-secret-key",
        }
    )
    return flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def temp_file_storage() -> Generator[Path, None, None]:
    """Create a temporary directory for file storage during tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "file_storage"
        storage_path.mkdir()
        yield storage_path


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing."""
    return [
        {
            "client": "Test Client 1",
            "purchase_date": "2022-08-10",
            "product": "Test Product 1",
            "price": 100.0,
        },
        {
            "client": "Test Client 2",
            "purchase_date": "2022-08-10",
            "product": "Test Product 2",
            "price": 200.0,
        },
    ]


@pytest.fixture
def test_date():
    """A test date for consistent testing."""
    return date(2022, 8, 10)


@pytest.fixture
def mock_auth_token(monkeypatch):
    """Mock AUTH_TOKEN environment variable."""
    monkeypatch.setenv("AUTH_TOKEN", "test-auth-token")


@pytest.fixture
def mock_log_key(monkeypatch):
    """Mock LOG_KEY environment variable."""
    monkeypatch.setenv("LOG_KEY", "test-log-key")
