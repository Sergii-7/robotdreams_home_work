from src.config import DEBUG_MODE, HOST, PORT
from src.flask_app.create_app import app
from src.flask_app.routes import admin_routers, api_routes, routers

routers.logger.debug("'routers' module imported")
admin_routers.logger.debug("'admin_routers' module imported")
api_routes.logger.debug("'api_routes' module imported")


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
