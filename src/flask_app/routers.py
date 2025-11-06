import shutil
from datetime import datetime
from pathlib import Path

from flask import jsonify, render_template, request, send_file
from flask import typing as flask_typing

from src.config import AUTH_TOKEN
from src.flask_app.create_app import app, csrf
from src.flask_app.form import DateReport
from src.services.jobs.job1.save_sales import save_sales_to_local_disk
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)

if not AUTH_TOKEN:
    logger.error("AUTH_TOKEN environment variable must be set")


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
    }
    if form.validate_on_submit():
        sale_date = form.data.get("sale_date")
        print(sale_date)
        if sale_date:
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
        else:
            data["msg"] = f"Немає даних за {sale_date}."
    return render_template(template_name_or_list="index.html", data=data)


@app.route("/health", methods=["GET"])
def health_check() -> flask_typing.ResponseReturnValue:
    """Проста перевірка стану сервісу"""
    return jsonify({"status": "ok"}), 200


@app.route("/v1/job1", methods=["POST"])
def job1() -> flask_typing.ResponseReturnValue:
    """
    Приймає JSON:
    {
      "date": "2022-08-09",
      "raw_dir": "/path/to/my_dir/raw/sales/2022-08-09"
    }
    Вимоги:
      1) raw_dir має закінчуватись датою (YYYY-MM-DD) і містити сегменти /raw/sales/
      2) Джоба ідемпотентна: перед записом очищаємо вміст raw_dir
    """
    data: dict = request.get_json(silent=True) or {}
    date_str = data.get("date")
    raw_dir_str = data.get("raw_dir")
    logger.debug(
        "Received job1 request with date=%s and raw_dir=%s", date_str, raw_dir_str
    )
    # 1) Перевірка дати
    if not date_str:
        return jsonify({"message": "date parameter missed"}), 400
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "date must be in format YYYY-MM-DD"}), 400
    # 2) Перевірка raw_dir формату та узгодженості з date
    if not raw_dir_str:
        return jsonify({"message": "raw_dir parameter missed"}), 400
    raw_dir = Path(raw_dir_str).resolve()
    # Вимога формату: .../raw/sales/YYYY-MM-DD
    # (a) останній сегмент == date
    if raw_dir.name != date_str:
        return (
            jsonify({"message": "raw_dir must end with the same date (YYYY-MM-DD)"}),
            400,
        )
    # (b) присутні сегменти 'raw' і 'sales' у батьківських
    parents = [p.name for p in raw_dir.parents]
    if "sales" not in parents or "raw" not in parents:
        return jsonify({"message": "raw_dir must contain .../raw/sales/<date>"}), 400
    try:
        # 3) Ідемпотентність: прибрати ВСЕ в середині raw_dir
        raw_dir.mkdir(parents=True, exist_ok=True)
        for child in raw_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink(missing_ok=True)
        # 4) Виклик бізнес-логіки (записуємо свіжі файли в порожню директорію)
        save_sales_to_local_disk(date_=date_obj, raw_dir=str(raw_dir))
    except Exception as e:
        logger.error("job failed: %s", str(e))
        return jsonify({"message": "failed to process job", "error": str(e)}), 500

    return jsonify({"message": "Data retrieved successfully from API"}), 201


# відключаємо CSRF для view (робимо після визначення функції)
csrf.exempt(job1)
