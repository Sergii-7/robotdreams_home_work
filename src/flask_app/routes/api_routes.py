from datetime import datetime

from flask import jsonify, request
from flask import typing as flask_typing

from src.config import AUTH_TOKEN
from src.flask_app.create_app import app, csrf
from src.services.jobs.job_1_and_2.save_sales import save_sales_to_local_disk
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)

if not AUTH_TOKEN:
    logger.error("AUTH_TOKEN environment variable must be set")


@app.route("/v1/api/job", methods=["POST"])
def job() -> flask_typing.ResponseReturnValue:
    """
    Приймає JSON:
    {
      "date": "2022-08-09",
      "to_stg": false
    }
    ps: Якщо to_stg=true, то крім JSON створює AVRO-файл у відповідній папці stg.
    --------------------------------------------------------------------------
    Example response (201 Created) if to_stg=false and data exists:
    {
      "message": "Data retrieved successfully from API for date 2022-08-09",
      "file_path": "/file_storage/raw/sales/2022-08-09/sales_2022-08-09.json"
    }
    ---
    Example response (201 Created) if to_stg=true and data exists:
    {
      "message": "Data retrieved successfully from API for date 2022-08-09",
      "file_path": "/file_storage/stg/sales/2022-08-09/sales_2022-08-09.avro"
    }
    --------------------------------------------------------------------------
    """
    data: dict = request.get_json(silent=True) or {}
    date_str = data.get("date")
    to_stg = data.get("to_stg", False)
    logger.debug("Received job request with date=%s and to_stg=%s", date_str, to_stg)
    # 1) Перевірка дати
    if not date_str:
        return jsonify({"message": "date parameter missed"}), 400
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "date must be in format YYYY-MM-DD"}), 400
    # 2) Виклик збереження даних
    try:
        file_path = save_sales_to_local_disk(date_=date_obj, to_stg=to_stg)
        if not file_path:
            return (
                jsonify({"message": f"No data found for date {date_str}"}),
                204,
            )
        return (
            jsonify(
                {
                    "message": f"Data retrieved successfully from API for date {date_str}",
                    "file_path": str(file_path),
                }
            ),
            201,
        )
    except Exception as e:
        logger.error("job failed: %s", str(e))
        return jsonify({"message": "failed to process job", "error": str(e)}), 500


# відключаємо CSRF
csrf.exempt(job)
