import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # ../src
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
FILE_LOG = os.path.join(LOGS_DIR, "app.log")
FILE_STORAGE = os.path.join(PROJECT_ROOT, "file_storage")
check_storage = os.path.exists(FILE_STORAGE)
if not check_storage:
    os.makedirs(FILE_STORAGE)

# Flask App data
PORT = 8081
DEBUG_MODE = False
if DEBUG_MODE:
    HOST = "localhost"
else:
    HOST = "0.0.0.0"
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "flask_app/static")
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, "flask_app/templates")
SECRET_KEY = os.environ.get("SECRET_KEY")  # for Flask-WTF CSRF protection
LOG_KEY = os.environ.get("LOG_KEY")  # for logging sensitive data masking

# Database config
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
