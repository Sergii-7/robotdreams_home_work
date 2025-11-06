from src.config import DEBUG_MODE, HOST, PORT
from src.flask_app import admin_routers  # noqa: F401
from src.flask_app import routers  # noqa: F401
from src.flask_app.create_app import app

routers.logger.debug("'routers' module imported")
admin_routers.logger.debug("'admin_routers' module imported")


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
