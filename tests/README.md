# Tests Documentation

## Overview
Comprehensive test suite for the Flask application and data processing services.

## Test Coverage

### Total Statistics
- **Total Tests**: 91
- **All Passing**: ✅ 100%
- **Code Coverage**: 94%

### Coverage by Module
- `src/flask_app/create_app.py`: 100%
- `src/flask_app/form.py`: 100%
- `src/flask_app/routes/admin_routers.py`: 100%
- `src/flask_app/routes/api_routes.py`: 97%
- `src/flask_app/routes/routers.py`: 100%
- `src/services/jobs/job1/fake_api_tool.py`: 85%
- `src/services/jobs/job1/save_sales.py`: 92%

## Test Files

### Flask App Tests

#### `test_flask_app.py` (6 tests)
Tests for Flask application initialization and configuration:
- App instance existence
- Secret key configuration
- CSRF protection initialization
- Template and static folder configuration
- App naming

#### `test_forms.py` (7 tests)
Tests for Flask-WTF forms:
- Form instantiation
- Field existence and types (sale_date, sale_date_stg, submit)
- Field validators (Optional)
- Submit button label

#### `test_routes.py` (11 tests)
Tests for main application routes:
- Health check endpoint (`/health`)
- Home page GET/POST requests (`/`)
- Form submission with different date formats
- File download (JSON/AVRO)
- Error handling
- IP address logging

#### `test_admin_routes.py` (7 tests)
Tests for admin routes:
- Log file download endpoint (`/log`)
- Authentication with LOG_KEY
- Access control (403 Forbidden on wrong key)
- Logging behavior

#### `test_api_routes.py` (14 tests)
Tests for REST API endpoints:
- Job endpoint (`/v1/api/job`)
- Date validation
- JSON/AVRO export via API
- Error handling (400, 500, 204)
- CSRF exemption
- Request/error logging

### Services Tests

#### `test_fake_api_tool.py` (15 tests)
Tests for external API integration:
- APITool initialization
- HTTP request handling
- Pagination logic
- Error handling (RequestException, HTTPError)
- Rate limiting (0.2s sleep between requests)
- Logging (debug, error)

#### `test_save_sales.py` (31 tests)
Tests for sales data export functionality:
- SalesExporter initialization
- JSON export to `raw/` directory
- AVRO export to `stg/` directory
- Schema management (default and custom)
- File naming conventions
- Directory creation
- Data validation
- Integration tests

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=src/flask_app --cov=src/services/jobs --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_flask_app.py -v
```

### Run specific test
```bash
pytest tests/test_flask_app.py::TestCreateApp::test_app_exists -v
```

## Test Structure

### Fixtures (in `conftest.py`)
- `app`: Flask app instance with test configuration
- `client`: Flask test client
- `temp_file_storage`: Temporary directory for file operations
- `sample_sales_data`: Sample data for testing
- `test_date`: Fixed date for consistent testing
- `mock_auth_token`: Mocked AUTH_TOKEN environment variable
- `mock_log_key`: Mocked LOG_KEY environment variable

### Test Organization
Tests are organized into classes by functionality:
- **Initialization tests**: Test object creation and configuration
- **Endpoint tests**: Test HTTP routes and responses
- **Business logic tests**: Test core functionality
- **Error handling tests**: Test exception scenarios
- **Integration tests**: Test complete workflows

## Mocking Strategy

### External Dependencies
- API requests mocked with `unittest.mock.patch`
- File system operations use `tmp_path` fixture
- Environment variables mocked when needed
- Logger calls verified with mock assertions

### Flask Testing
- CSRF disabled for easier testing
- Test configuration separate from production
- Routes imported to ensure registration

## Key Testing Patterns

### 1. Happy Path Testing
```python
def test_export_json_only(self, temp_file_storage, sample_sales_data):
    mock_api = Mock()
    mock_api.get_sales.return_value = sample_sales_data
    exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
    result = exporter.export(for_date=date(2022, 8, 10), to_stg=False)
    assert result is not None
    assert result.exists()
```

### 2. Error Handling
```python
def test_get_sales_handles_request_exception(self, mock_sleep, mock_get):
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Error")
    api = APITool()
    result = api.get_sales(date_=date(2022, 8, 9))
    assert isinstance(result, list)  # Should gracefully return empty/partial data
```

### 3. Side Effects Verification
```python
def test_home_logs_ip_address(self, client):
    with patch("src.flask_app.routes.routers.logger") as mock_logger:
        response = client.get("/")
        mock_logger.info.assert_called()  # Verify logging occurred
```

## Notes

- All tests are independent and can run in any order
- Tests use mocking to avoid external dependencies
- Temporary directories are automatically cleaned up
- Flask app context is properly managed in form tests
- Routes are registered before tests run via conftest.py imports
