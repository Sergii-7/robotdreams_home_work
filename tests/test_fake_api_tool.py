"""Tests for fake_api_tool.py - APITool class."""

from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.services.jobs.job1.fake_api_tool import APITool


class TestAPIToolInit:
    """Test APITool initialization."""

    def test_api_tool_initialization(self):
        """Test that APITool initializes correctly."""
        api = APITool()
        assert api.host == "https://fake-api-vycpfa6oca-uc.a.run.app"
        assert "Authorization" in api.headers

    def test_api_tool_has_correct_host(self):
        """Test that APITool has correct host."""
        api = APITool()
        assert "fake-api-vycpfa6oca-uc.a.run.app" in api.host
        assert api.host.startswith("https://")


class TestAPIToolGetOnePage:
    """Test APITool.get_one_page method."""

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    def test_get_one_page_success(self, mock_get):
        """Test successful get_one_page request."""
        mock_response = Mock()
        mock_response.json.return_value = [{"test": "data"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_one_page(date_=date(2022, 8, 9), page=1)

        assert result == [{"test": "data"}]
        mock_get.assert_called_once()
        assert "2022-08-09" in str(mock_get.call_args)
        assert "page" in str(mock_get.call_args)

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    def test_get_one_page_with_different_page(self, mock_get):
        """Test get_one_page with different page number."""
        mock_response = Mock()
        mock_response.json.return_value = [{"page": 2}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_one_page(date_=date(2022, 8, 9), page=2)

        assert result == [{"page": 2}]
        # Verify page parameter is passed correctly
        call_args = mock_get.call_args
        assert call_args[1]["params"]["page"] == "2"

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    def test_get_one_page_with_auth_header(self, mock_get):
        """Test that get_one_page includes auth header."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        api.get_one_page(date_=date(2022, 8, 9), page=1)

        call_args = mock_get.call_args
        assert "Authorization" in call_args[1]["headers"]

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    def test_get_one_page_raises_http_error(self, mock_get):
        """Test get_one_page when HTTP error occurs."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        api = APITool()
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_one_page(date_=date(2022, 8, 9), page=1)


class TestAPIToolGetSales:
    """Test APITool.get_sales method."""

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_single_page(self, mock_sleep, mock_get):
        """Test get_sales with single page of data."""
        mock_response = Mock()
        mock_response.json.side_effect = [
            [{"client": "Test", "price": 100}],
            [],  # Empty response to stop pagination
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        assert len(result) == 1
        assert result[0]["client"] == "Test"
        assert mock_get.call_count >= 1

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_multiple_pages(self, mock_sleep, mock_get):
        """Test get_sales with multiple pages of data."""
        mock_response = Mock()
        mock_response.json.side_effect = [
            [{"client": "Client1", "price": 100}],
            [{"client": "Client2", "price": 200}],
            [{"client": "Client3", "price": 300}],
            [],  # Empty response to stop
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        assert len(result) == 3
        assert result[0]["client"] == "Client1"
        assert result[1]["client"] == "Client2"
        assert result[2]["client"] == "Client3"

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_no_data(self, mock_sleep, mock_get):
        """Test get_sales when no data is available."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        assert result == []

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_handles_request_exception(self, mock_sleep, mock_get):
        """Test get_sales handles RequestException."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException("Connection error")
        )
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        # Should return empty list or partial data before error
        assert isinstance(result, list)

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_handles_unexpected_exception(self, mock_sleep, mock_get):
        """Test get_sales handles unexpected exceptions."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        # Should handle exception and return what was collected
        assert isinstance(result, list)

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_stops_on_non_list_response(self, mock_sleep, mock_get):
        """Test get_sales stops when response is not a list."""
        mock_response = Mock()
        mock_response.json.side_effect = [
            [{"client": "Client1"}],
            {"error": "Invalid"},  # Not a list
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        # Should only include the first page
        assert len(result) == 1
        assert result[0]["client"] == "Client1"

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_rate_limiting(self, mock_sleep, mock_get):
        """Test that get_sales implements rate limiting."""
        mock_response = Mock()
        mock_response.json.side_effect = [
            [{"client": "Client1"}],
            [{"client": "Client2"}],
            [],
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = APITool()
        result = api.get_sales(date_=date(2022, 8, 9))

        # Should sleep between requests
        assert mock_sleep.call_count >= 1
        # Check sleep duration is 0.2 seconds
        mock_sleep.assert_called_with(0.2)

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_logs_debug_info(self, mock_sleep, mock_get):
        """Test that get_sales logs debug information."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch("src.services.jobs.job1.fake_api_tool.logger") as mock_logger:
            api = APITool()
            api.get_sales(date_=date(2022, 8, 9))

            # Should log debug info about fetching pages
            mock_logger.debug.assert_called()

    @patch("src.services.jobs.job1.fake_api_tool.requests.get")
    @patch("src.services.jobs.job1.fake_api_tool.time.sleep")
    def test_get_sales_logs_errors(self, mock_sleep, mock_get):
        """Test that get_sales logs errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException("Error")
        )
        mock_get.return_value = mock_response

        with patch("src.services.jobs.job1.fake_api_tool.logger") as mock_logger:
            api = APITool()
            api.get_sales(date_=date(2022, 8, 9))

            # Should log error
            mock_logger.error.assert_called()
