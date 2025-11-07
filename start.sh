#!/bin/bash

# DEBUG MODE:
flask --app main:app run --host 0.0.0.0 --port 8081 --debug

# PRODUCTION MODE:
# uv run gunicorn -b 0.0.0.0:8081 main:app --workers 2
