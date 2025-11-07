# robotdreams_home_work
### home work for robotdreams

## TESTING THE FLASK APPLICATION LOCALLY
### HOST=http://localhost:8080

### 1. Run the application in localhost:8081
```bash
flask --app main:app run --host 0.0.0.0 --port 8081 --debug
```
### 2. Testing the application api in localhost:8081 with curl commands
```bash
curl -X POST http://localhost:8081/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": true}'
```
```bash
curl -X POST http://localhost:8081/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": false}'
```

## CLOUD TESTING THE FLASK APPLICATION
### HOST=https://sb-homework-rd-og3n9.ondigitalocean.app/

### Testing the application API in CLOUD with curl commands
```bash
curl -X POST https://sb-homework-rd-og3n9.ondigitalocean.app/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": true}'
```
```bash
curl -X POST https://sb-homework-rd-og3n9.ondigitalocean.app/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": false}'
```

## Running Tests (see tests/README.md for details)

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
