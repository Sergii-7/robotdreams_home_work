"""Tests for API routes."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient


class TestJobAPIRoute:
    """Test /v1/api/job endpoint."""

    def test_job_endpoint_exists(self, client: FlaskClient):
        """Test that /v1/api/job endpoint exists."""
        response = client.post("/v1/api/job", json={})
        # Should return 400 for missing date, not 404
        assert response.status_code != 404

    def test_job_post_without_date(self, client: FlaskClient):
        """Test POST /v1/api/job without date parameter."""
        response = client.post("/v1/api/job", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert "date parameter missed" in data["message"]

    def test_job_post_with_invalid_date_format(self, client: FlaskClient):
        """Test POST /v1/api/job with invalid date format."""
        response = client.post("/v1/api/job", json={"date": "2022/08/09"})
        assert response.status_code == 400
        data = response.get_json()
        assert "format YYYY-MM-DD" in data["message"]

    def test_job_post_with_invalid_date(self, client: FlaskClient):
        """Test POST /v1/api/job with invalid date."""
        response = client.post("/v1/api/job", json={"date": "2022-13-45"})
        assert response.status_code == 400
        data = response.get_json()
        assert "format YYYY-MM-DD" in data["message"]

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_post_with_valid_date_success(
        self, mock_save_sales, client: FlaskClient, tmp_path: Path
    ):
        """Test POST /v1/api/job with valid date and successful data retrieval."""
        test_file = tmp_path / "sales_2022-08-09.json"
        test_file.write_text('{"test": "data"}')
        mock_save_sales.return_value = str(test_file)

        response = client.post("/v1/api/job", json={"date": "2022-08-09"})
        assert response.status_code == 201
        data = response.get_json()
        assert "Data retrieved successfully" in data["message"]
        assert "file_path" in data
        mock_save_sales.assert_called_once()

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_post_with_to_stg_false(
        self, mock_save_sales, client: FlaskClient, tmp_path: Path
    ):
        """Test POST /v1/api/job with to_stg=false."""
        test_file = tmp_path / "sales_2022-08-09.json"
        test_file.write_text('{"test": "data"}')
        mock_save_sales.return_value = str(test_file)

        response = client.post(
            "/v1/api/job", json={"date": "2022-08-09", "to_stg": False}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "Data retrieved successfully" in data["message"]
        mock_save_sales.assert_called_once_with(date_=date(2022, 8, 9), to_stg=False)

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_post_with_to_stg_true(
        self, mock_save_sales, client: FlaskClient, tmp_path: Path
    ):
        """Test POST /v1/api/job with to_stg=true."""
        test_file = tmp_path / "sales_2022-08-09.avro"
        test_file.write_bytes(b"test avro data")
        mock_save_sales.return_value = str(test_file)

        response = client.post(
            "/v1/api/job", json={"date": "2022-08-09", "to_stg": True}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "Data retrieved successfully" in data["message"]
        assert ".avro" in data["file_path"]
        mock_save_sales.assert_called_once_with(date_=date(2022, 8, 9), to_stg=True)

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_post_no_data_found(self, mock_save_sales, client: FlaskClient):
        """Test POST /v1/api/job when no data is found."""
        mock_save_sales.return_value = None

        response = client.post("/v1/api/job", json={"date": "2022-08-09"})
        assert response.status_code == 204
        # 204 No Content doesn't have a JSON body
        mock_save_sales.assert_called_once()

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_post_exception_handling(self, mock_save_sales, client: FlaskClient):
        """Test POST /v1/api/job when an exception occurs."""
        mock_save_sales.side_effect = Exception("Test error")

        response = client.post("/v1/api/job", json={"date": "2022-08-09"})
        assert response.status_code == 500
        data = response.get_json()
        assert "failed to process job" in data["message"]
        assert "error" in data

    def test_job_post_with_empty_json(self, client: FlaskClient):
        """Test POST /v1/api/job with empty JSON body."""
        response = client.post("/v1/api/job", json={})
        assert response.status_code == 400

    def test_job_post_without_json_content_type(self, client: FlaskClient):
        """Test POST /v1/api/job without JSON content type."""
        response = client.post("/v1/api/job", data="date=2022-08-09")
        assert response.status_code == 400

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_logs_debug_on_request(self, mock_save_sales, client: FlaskClient):
        """Test that job endpoint logs debug information."""
        mock_save_sales.return_value = None

        with patch("src.flask_app.routes.api_routes.logger") as mock_logger:
            response = client.post("/v1/api/job", json={"date": "2022-08-09"})
            # Check that debug was logged
            mock_logger.debug.assert_called()

    @patch("src.flask_app.routes.api_routes.save_sales_to_local_disk")
    def test_job_logs_error_on_exception(self, mock_save_sales, client: FlaskClient):
        """Test that job endpoint logs error on exception."""
        mock_save_sales.side_effect = Exception("Test error")

        with patch("src.flask_app.routes.api_routes.logger") as mock_logger:
            response = client.post("/v1/api/job", json={"date": "2022-08-09"})
            # Check that error was logged
            mock_logger.error.assert_called()

    def test_csrf_exemption_on_job_endpoint(self, client: FlaskClient):
        """Test that CSRF is exempted for /v1/api/job endpoint."""
        # This endpoint should work without CSRF token
        response = client.post("/v1/api/job", json={})
        # Should return 400 for missing date, not CSRF error
        assert response.status_code == 400
        data = response.get_json()
        assert "date parameter missed" in data["message"]
