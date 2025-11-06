from flask import abort, redirect, request, send_file, url_for

from src.config import FILE_LOG, LOG_KEY
from src.flask_app.create_app import app
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)


@app.route("/log", methods=["GET", "POST"])
def log():
    """
    Якщо GET — редірект на home.
    Якщо POST — перевіряємо ключ з форми і якщо ОК — відправляємо файл з логами і редірект на home.
    """
    if request.method == "POST":
        # беремо ключ із тіла форми (не з JS)
        supplied = request.form.get("log_key")
        if supplied and supplied == LOG_KEY:
            logger.info("Log file requested and key accepted.")
            return send_file(path_or_file=FILE_LOG, download_name="app.log")
        else:
            # НЕ даємо детальну причину (security)
            logger.warning("Log file not accepted.")
            abort(403)
    # GET — або редірект, або форма (за необхідності)
    return redirect(url_for("home"))
