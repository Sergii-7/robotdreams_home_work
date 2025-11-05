import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # ../src
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
FILE_LOG = os.path.join(LOGS_DIR, "app.log")

# Flask App data
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "app/static")
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, "app/templates")
# DIR_JSON_DATA = os.path.join(PROJECT_ROOT, "service/json_data")
