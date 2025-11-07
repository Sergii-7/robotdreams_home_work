"""Tests for main Flask routes."""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client: FlaskClient):
        """Test that /health endpoint returns 200 status."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_json(self, client: FlaskClient):
        """Test that /health endpoint returns JSON."""
        response = client.get("/health")
        assert response.content_type == "application/json"

    def test_health_check_status_ok(self, client: FlaskClient):
        """Test that /health endpoint returns status ok."""
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "ok"


class TestHomeRoute:
    """Test home route endpoint."""

    def test_home_get_returns_200(self, client: FlaskClient):
        """Test that GET / returns 200 status."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_get_renders_template(self, client: FlaskClient):
        """Test that GET / renders the index.html template."""
        response = client.get("/")
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_home_post_without_date(self, client: FlaskClient):
        """Test POST to / without date data."""
        response = client.post("/", data={})
        # Form validation should fail or return to same page
        assert response.status_code in [200, 302]

    @patch("src.flask_app.routes.routers.save_sales_to_local_disk")
    def test_home_post_with_valid_date_json(
        self, mock_save_sales, client: FlaskClient, tmp_path: Path
    ):
        """Test POST to / with valid date for JSON download."""
        # Create a temporary file to simulate the saved file
        test_file = tmp_path / "test_sales.json"
        test_file.write_text('{"test": "data"}')
        mock_save_sales.return_value = str(test_file)

        response = client.post(
            "/",
            data={
                "sale_date": "2022-08-10",
                "sale_date_stg": "",
            },
            follow_redirects=False,
        )

        # Should return the file or 200
        assert response.status_code in [200, 302]
        mock_save_sales.assert_called_once()

    @patch("src.flask_app.routes.routers.save_sales_to_local_disk")
    def test_home_post_with_valid_date_avro(
        self, mock_save_sales, client: FlaskClient, tmp_path: Path
    ):
        """Test POST to / with valid date for AVRO download."""
        # Create a temporary file to simulate the saved file
        test_file = tmp_path / "test_sales.avro"
        test_file.write_bytes(b"test avro data")
        mock_save_sales.return_value = str(test_file)

        response = client.post(
            "/",
            data={
                "sale_date": "",
                "sale_date_stg": "2022-08-10",
            },
            follow_redirects=False,
        )

        # Should return the file or 200
        assert response.status_code in [200, 302]
        mock_save_sales.assert_called_once()

    @patch("src.flask_app.routes.routers.save_sales_to_local_disk")
    def test_home_post_no_data_found(self, mock_save_sales, client: FlaskClient):
        """Test POST to / when no data is found for the date."""
        mock_save_sales.return_value = None

        response = client.post(
            "/",
            data={
                "sale_date": "2022-08-10",
                "sale_date_stg": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        # Should flash a message about no data
        mock_save_sales.assert_called_once()

    @patch("src.flask_app.routes.routers.save_sales_to_local_disk")
    def test_home_post_exception_handling(self, mock_save_sales, client: FlaskClient):
        """Test POST to / when an exception occurs."""
        mock_save_sales.side_effect = Exception("Test error")

        response = client.post(
            "/",
            data={
                "sale_date": "2022-08-10",
                "sale_date_stg": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        # Should flash an error message
        mock_save_sales.assert_called_once()

    def test_home_logs_ip_address(self, client: FlaskClient):
        """Test that home route logs IP address."""
        with patch("src.flask_app.routes.routers.logger") as mock_logger:
            response = client.get("/")
            assert response.status_code == 200
            # Check that logger.info was called
            mock_logger.info.assert_called()
