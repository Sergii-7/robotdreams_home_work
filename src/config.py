import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # ../src
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
FILE_LOG = os.path.join(LOGS_DIR, "app.log")

# Flask App data
PORT = 8081
DEBUG_MODE = True
if DEBUG_MODE:
    HOST = "localhost"
else:
    HOST = "0.0.0.0"
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "flask_app/static")
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, "flask_app/templates")
FILE_STORAGE = os.path.join(PROJECT_ROOT, "src/file_storage")
SECRET_KEY = os.environ.get("SECRET_KEY")  # for Flask-WTF CSRF protection
LOG_KEY = os.environ.get("LOG_KEY")
