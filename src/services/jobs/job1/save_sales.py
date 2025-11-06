import json
from datetime import date
from pathlib import Path

from src.services.jobs.job1.fake_api_tool import APITool


def save_sales_to_local_disk(date_: date, raw_dir: str):
    """
    Get sales data from the API for a specific date and save it to a local JSON file.
    """

    api_tool = APITool()
    sales_data = api_tool.get_sales(date_=date_)

    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    file_path = raw_path / f"sales_{date_.isoformat()}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(sales_data, f, ensure_ascii=False, indent=4)
