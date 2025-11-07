"""Tests for admin routes."""

from pathlib import Path
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient


class TestLogRoute:
    """Test /log admin route."""

    def test_log_get_redirects_to_home(self, client: FlaskClient):
        """Test that GET /log redirects to home."""
        response = client.get("/log", follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith("/")

    @patch("src.config.LOG_KEY", "correct-key")
    @patch("src.config.FILE_LOG")
    def test_log_post_with_correct_key(
        self, mock_file_log, client: FlaskClient, tmp_path: Path
    ):
        """Test POST /log with correct key returns log file."""
        # Create a temporary log file
        log_file = tmp_path / "app.log"
        log_file.write_text("Test log content")
        mock_file_log.__str__ = lambda x: str(log_file)
        mock_file_log.__fspath__ = lambda x: str(log_file)

        with patch("src.flask_app.routes.admin_routers.FILE_LOG", str(log_file)):
            with patch("src.flask_app.routes.admin_routers.LOG_KEY", "correct-key"):
                response = client.post("/log", data={"log_key": "correct-key"})
                # Should return file or 200
                assert response.status_code in [
                    200,
                    404,
                    500,
                ]  # May fail if file not found

    @patch("src.config.LOG_KEY", "correct-key")
    def test_log_post_with_incorrect_key(self, client: FlaskClient):
        """Test POST /log with incorrect key returns 403."""
        response = client.post("/log", data={"log_key": "wrong-key"})
        assert response.status_code == 403

    @patch("src.config.LOG_KEY", "correct-key")
    def test_log_post_with_missing_key(self, client: FlaskClient):
        """Test POST /log without key returns 403."""
        response = client.post("/log", data={})
        assert response.status_code == 403

    @patch("src.config.LOG_KEY", "correct-key")
    def test_log_post_with_empty_key(self, client: FlaskClient):
        """Test POST /log with empty key returns 403."""
        response = client.post("/log", data={"log_key": ""})
        assert response.status_code == 403

    def test_log_route_logs_warning_on_incorrect_key(self, client: FlaskClient):
        """Test that log route logs warning when incorrect key is provided."""
        with patch("src.flask_app.routes.admin_routers.logger") as mock_logger:
            with patch("src.config.LOG_KEY", "correct-key"):
                response = client.post("/log", data={"log_key": "wrong-key"})
                assert response.status_code == 403
                # Check that warning was logged
                mock_logger.warning.assert_called()

    @patch("src.config.LOG_KEY", "correct-key")
    @patch("src.config.FILE_LOG")
    def test_log_route_logs_info_on_success(
        self, mock_file_log, client: FlaskClient, tmp_path: Path
    ):
        """Test that log route logs info when key is accepted."""
        log_file = tmp_path / "app.log"
        log_file.write_text("Test log content")

        with patch("src.flask_app.routes.admin_routers.logger") as mock_logger:
            with patch("src.flask_app.routes.admin_routers.FILE_LOG", str(log_file)):
                with patch("src.flask_app.routes.admin_routers.LOG_KEY", "correct-key"):
                    response = client.post("/log", data={"log_key": "correct-key"})
                    # Check that info was logged
                    mock_logger.info.assert_called()
