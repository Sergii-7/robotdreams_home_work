import time
from datetime import date
from typing import Any, Dict, List, Optional

import requests

from src.config import AUTH_TOKEN
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)


class APITool:
    def __init__(self):
        self.host = "https://fake-api-vycpfa6oca-uc.a.run.app"
        self.headers = {"Authorization": AUTH_TOKEN}

    def _get(self, endpoint: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        url = f"{self.host}/{endpoint}"
        resp = requests.get(url=url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_one_page(self, date_: date, page: int = 1) -> List[Dict[str, Any]]:
        """Get sales data from the API."""
        params = {
            "date": date_.isoformat(),
            "page": str(page),
        }
        return self._get(endpoint="sales", params=params)

    def get_sales(self, date_: date) -> List[Dict[str, Any]]:
        """Get all sales data from the API for a specific date."""
        all_data = []
        page = 1
        while page <= 1000:  # Limit to avoid infinite loop
            try:
                logger.debug(f"Fetching page {page} for date {date_}")
                data = self.get_one_page(date_=date_, page=page)
            except requests.exceptions.RequestException as err:
                logger.error(f"Error fetching data from API: {err}")
                break
            except Exception as err:
                logger.error(f"Unexpected error: {err}")
                break
            if not data or not isinstance(data, list):
                break
            all_data.extend(data)
            page += 1
            time.sleep(0.2)  # To avoid hitting rate limits
        return all_data

    def run(self, date_: date, raw_dir: Optional[str] = None):
        """
        Run the API tool to get sales data for a specific date, and saves data to a local file JSON.
        """
        ...


def _demo():
    """Demo function to show how to use the APITool class."""
    api_tool = APITool()
    sales_data = api_tool.get_sales(date_=date(2022, 8, 9))
    print(f"Retrieved {len(sales_data)} sales records.")
    for record in sales_data:
        print(record)


if __name__ == "__main__":
    """Testing this module."""
    _demo()
