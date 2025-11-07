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
### HOST=...

### Testing the application API in CLOUD with curl commands
```bash
curl -X POST http://localhost:8081/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": true}'
```
```bash
curl -X POST http://localhost:8081/v1/api/job -H "Content-Type: application/json" -d '{"date": "2022-08-10", "to_stg": false}'
```
