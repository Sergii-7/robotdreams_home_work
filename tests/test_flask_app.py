"""Tests for Flask app initialization and configuration."""

import pytest
from flask import Flask

from src.flask_app.create_app import app, csrf


class TestCreateApp:
    """Test Flask application creation and configuration."""

    def test_app_exists(self):
        """Test that the Flask app instance exists."""
        assert app is not None
        assert isinstance(app, Flask)

    def test_app_has_secret_key(self, app):
        """Test that the app has a SECRET_KEY configured."""
        assert app.config.get("SECRET_KEY") is not None

    def test_csrf_protection_initialized(self):
        """Test that CSRF protection is initialized."""
        assert csrf is not None

    def test_template_folder_configured(self, app):
        """Test that template folder is configured."""
        assert app.template_folder is not None

    def test_static_folder_configured(self, app):
        """Test that static folder is configured."""
        assert app.static_folder is not None

    def test_app_name(self, app):
        """Test that app has the correct name."""
        assert app.name == "src.flask_app.create_app"
