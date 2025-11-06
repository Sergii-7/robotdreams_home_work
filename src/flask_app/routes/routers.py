from flask import jsonify, render_template, request, send_file
from flask import typing as flask_typing

from src.flask_app.create_app import app
from src.flask_app.form import DateReport
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)


@app.route("/health", methods=["GET"])
def health_check() -> flask_typing.ResponseReturnValue:
    """Проста перевірка стану сервісу"""
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET", "POST"])
def home():
    """Main page to getting the Excel file."""
    ip_address = request.headers.get("X-Forwarded-For") or request.remote_addr
    logger.info(msg=f"ipAddress={ip_address}: '/'")
    form = DateReport()
    data = {
        "title": "SB",
        "page": "home",
        "form": form,
        "msg": None,
        "msg_stg": None,
    }
    if form.validate_on_submit():
        sale_date = form.data.get("sale_date")
        sale_date_stg = form.data.get("sale_date_stg")
        print(type(sale_date), str(sale_date))
        print(type(sale_date_stg), str(sale_date_stg))
        if sale_date or sale_date_stg:
            try:
                # TODO: Виклик бізнес-логіки для отримання JSON файлу
                json_file = None
                if json_file:
                    download_name = f"sales_{sale_date}.json"
                    return send_file(
                        path_or_file=json_file, download_name=download_name
                    )
                else:
                    data["msg"] = f"Немає даних за {sale_date}."
            except Exception as e:
                msg = str(e)
                logger.error(f"Error processing date {sale_date}: {msg}")
                data["msg"] = f"Сталося помилка:<p>{msg}</p>"
    return render_template(template_name_or_list="index.html", data=data)
