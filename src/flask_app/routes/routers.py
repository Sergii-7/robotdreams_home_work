from flask import flash, jsonify, render_template, request, send_file
from flask import typing as flask_typing

from src.flask_app.create_app import app
from src.flask_app.form import DateReport
from src.services.jobs.job1.save_sales import save_sales_to_local_disk
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
    logger.info(f"ipAddress={ip_address}")
    form = DateReport()
    data = {"title": "SB", "page": "home", "form": form}
    if form.validate_on_submit():
        sale_date = form.data.get("sale_date")
        sale_date_stg = form.data.get("sale_date_stg")
        sale_date = sale_date if sale_date else sale_date_stg
        logger.info(
            "Form submitted with sale_date=%s, sale_date_stg=%s",
            sale_date,
            sale_date_stg,
        )
        try:
            file_ = save_sales_to_local_disk(
                sale_date, to_stg=True if sale_date_stg else False
            )
            format_ = "avro" if sale_date_stg else "json"
            if file_:
                return send_file(
                    path_or_file=file_,
                    as_attachment=True,
                    download_name=f"sales_{sale_date}.{format_}",
                    mimetype=f"application/{format_}",
                )
            else:
                flash(
                    f"<h3 style='color: red';>немає даних за <p>{sale_date}</p></h3>",
                    "danger",
                )
        except Exception as e:
            logger.error(f"Error processing date {sale_date}: {e}")
            flash(f"<h3 style='color: red';>сталося помилка: <p>{e}</p></h3>", "error")
    return render_template(template_name_or_list="index.html", data=data)
