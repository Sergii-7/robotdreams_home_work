from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

import fastavro

from src.config import FILE_STORAGE
from src.services.jobs.job_1_and_2.fake_api_tool import APITool
from src.services.loggers.py_logger import get_logger

logger = get_logger(__name__)


class SalesExporter:
    """
    Експортер продажів у локальне сховище:
    - запис JSON у .../raw/sales/YYYY-MM-DD/
    - опційно конвертує у AVRO (STG) у .../stg/sales/YYYY-MM-DD/
    """

    # ✅ Базова схема, якщо .avsc ще не поклали у репозиторій
    DEFAULT_SALES_SCHEMA = {
        "type": "record",
        "name": "SaleRecord",
        "fields": [
            {"name": "client", "type": "string"},
            {"name": "purchase_date", "type": "string"},
            {"name": "product", "type": "string"},
            {"name": "price", "type": "double"},
        ],
    }

    def __init__(
        self,
        file_storage: Union[str, Path],
        schema_file: Optional[Union[str, Path]] = None,
        api_tool: Optional[APITool] = None,
    ) -> None:
        self.file_storage = Path(file_storage).resolve()
        self.api = api_tool or APITool()
        # шлях до .avsc: за замовчуванням поруч із цим модулем у підпапці schemas/
        self.schema_file = (
            Path(schema_file).resolve()
            if schema_file
            else Path(__file__).resolve().parent / "schemas" / "sales_schema.avsc"
        )

    # ---------- публічний API ----------

    def export(self, for_date: date, to_stg: bool = False) -> Optional[Path]:
        """
        Отримати sales за дату і зберегти як JSON (+ опц. AVRO/STG).
        :return: шлях до створеного файлу (JSON або AVRO), або None якщо даних нема.
        """
        sales_data = self.api.get_sales(date_=for_date)
        if not sales_data:
            logger.warning("No sales data found for date %s", for_date)
            return None

        json_path = self._write_json(for_date, sales_data)
        if not to_stg:
            return json_path

        return self._json_to_avro(json_path=json_path, for_date=for_date)

    # ---------- приватні методи ----------

    def _ensure_schema(self) -> Dict[str, Any]:
        """Прочитати схему з файлу, створити дефолтну якщо її немає."""
        self.schema_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.schema_file.exists():
            with self.schema_file.open("w", encoding="utf-8") as f:
                json.dump(self.DEFAULT_SALES_SCHEMA, f, ensure_ascii=False, indent=2)
            logger.warning(
                "AVRO schema missing. Created default at: %s", self.schema_file
            )

        with self.schema_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, for_date: date, records: Any) -> Path:
        """Записати JSON у .../raw/sales/YYYY-MM-DD/sales_YYYY-MM-DD.json"""
        raw_dir = self.file_storage / "raw" / "sales" / for_date.isoformat()
        raw_dir.mkdir(parents=True, exist_ok=True)

        json_path = raw_dir / f"sales_{for_date.isoformat()}.json"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)

        logger.info("✅ JSON-файл створено: %s", json_path)
        return json_path

    def _json_to_avro(self, json_path: Path, for_date: date) -> Path:
        """
        Конвертувати JSON -> AVRO (STG) у .../stg/sales/YYYY-MM-DD/sales_YYYY-MM-DD.avro
        """
        schema = self._ensure_schema()

        # читаємо дані
        with json_path.open("r", encoding="utf-8") as f:
            records = json.load(f)
        if isinstance(records, dict):
            records = [records]
        assert isinstance(
            records, Iterable
        ), "Records must be iterable of dicts for Avro writer"

        # куди писати .avro
        stg_dir = self.file_storage / "stg" / "sales" / for_date.isoformat()
        stg_dir.mkdir(parents=True, exist_ok=True)
        avro_path = stg_dir / f"sales_{for_date.isoformat()}.avro"

        # пишемо avro
        with avro_path.open("wb") as out:
            fastavro.writer(out, schema, records)

        logger.info("✅ STG-файл створено: %s", avro_path)
        return avro_path


# ---------- тонка функція-обгортка під існуючий інтерфейс ----------


def save_sales_to_local_disk(
    date_: date,
    to_stg: bool = False,
) -> Optional[str]:
    """
    Отримати sales за дату і зберегти як JSON (+ опц. STG/Avro).
    Повертає str-шлях до створеного файлу або None.
    """
    exporter = SalesExporter(file_storage=FILE_STORAGE)
    result = exporter.export(for_date=date_, to_stg=to_stg)
    return str(result) if result else None


# ---------- demo ----------

if __name__ == "__main__":
    """Test/demo."""
    d = date(2022, 8, 11)
    print(save_sales_to_local_disk(d, to_stg=False))
    print(save_sales_to_local_disk(d, to_stg=True))
