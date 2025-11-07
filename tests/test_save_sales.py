"""Tests for save_sales.py - SalesExporter and save_sales_to_local_disk."""

import json
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import fastavro
import pytest

from src.services.jobs.job1.save_sales import (
    SalesExporter,
    save_sales_to_local_disk,
)


class TestSalesExporterInit:
    """Test SalesExporter initialization."""

    def test_sales_exporter_init(self, temp_file_storage):
        """Test SalesExporter initialization."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        assert exporter.file_storage == temp_file_storage.resolve()
        assert exporter.api is not None

    def test_sales_exporter_with_custom_api(self, temp_file_storage):
        """Test SalesExporter initialization with custom API."""
        mock_api = Mock()
        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        assert exporter.api == mock_api

    def test_sales_exporter_schema_file_default(self, temp_file_storage):
        """Test that default schema file path is set correctly."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        assert exporter.schema_file.name == "sales_schema.avsc"
        assert "schemas" in str(exporter.schema_file)

    def test_sales_exporter_with_custom_schema_file(self, temp_file_storage, tmp_path):
        """Test SalesExporter with custom schema file."""
        schema_file = tmp_path / "custom_schema.avsc"
        exporter = SalesExporter(
            file_storage=temp_file_storage, schema_file=schema_file
        )
        assert exporter.schema_file == schema_file.resolve()


class TestSalesExporterExport:
    """Test SalesExporter.export method."""

    def test_export_json_only(self, temp_file_storage, sample_sales_data):
        """Test export with JSON only (to_stg=False)."""
        mock_api = Mock()
        mock_api.get_sales.return_value = sample_sales_data

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        assert result is not None
        assert result.exists()
        assert result.suffix == ".json"
        assert "raw/sales/2022-08-10" in str(result)

        # Verify file content
        with result.open("r") as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["client"] == "Test Client 1"

    def test_export_with_stg(self, temp_file_storage, sample_sales_data):
        """Test export with STG/AVRO (to_stg=True)."""
        mock_api = Mock()
        mock_api.get_sales.return_value = sample_sales_data

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=True)

        assert result is not None
        assert result.exists()
        assert result.suffix == ".avro"
        assert "stg/sales/2022-08-10" in str(result)

        # Verify JSON file was also created
        json_file = (
            temp_file_storage / "raw" / "sales" / "2022-08-10" / "sales_2022-08-10.json"
        )
        assert json_file.exists()

    def test_export_no_data(self, temp_file_storage):
        """Test export when API returns no data."""
        mock_api = Mock()
        mock_api.get_sales.return_value = []

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        assert result is None

    def test_export_none_data(self, temp_file_storage):
        """Test export when API returns None."""
        mock_api = Mock()
        mock_api.get_sales.return_value = None

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        assert result is None

    def test_export_logs_warning_on_no_data(self, temp_file_storage):
        """Test that export logs warning when no data is found."""
        mock_api = Mock()
        mock_api.get_sales.return_value = None

        with patch("src.services.jobs.job1.save_sales.logger") as mock_logger:
            exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
            exporter.export(for_date=date(2022, 8, 10), to_stg=False)

            mock_logger.warning.assert_called()


class TestSalesExporterWriteJson:
    """Test SalesExporter._write_json method."""

    def test_write_json_creates_directory(self, temp_file_storage, sample_sales_data):
        """Test that _write_json creates necessary directories."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        result = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        assert result.parent.exists()
        assert result.parent.name == "2022-08-10"

    def test_write_json_file_content(self, temp_file_storage, sample_sales_data):
        """Test that _write_json writes correct JSON content."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        result = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        with result.open("r") as f:
            data = json.load(f)
            assert data == sample_sales_data

    def test_write_json_file_name(self, temp_file_storage, sample_sales_data):
        """Test that _write_json creates file with correct name."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        result = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        assert result.name == "sales_2022-08-10.json"

    def test_write_json_logs_success(self, temp_file_storage, sample_sales_data):
        """Test that _write_json logs success message."""
        with patch("src.services.jobs.job1.save_sales.logger") as mock_logger:
            exporter = SalesExporter(file_storage=temp_file_storage)
            exporter._write_json(for_date=date(2022, 8, 10), records=sample_sales_data)

            mock_logger.info.assert_called()


class TestSalesExporterEnsureSchema:
    """Test SalesExporter._ensure_schema method."""

    def test_ensure_schema_creates_default(self, temp_file_storage):
        """Test that _ensure_schema creates default schema if not exists."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        schema = exporter._ensure_schema()

        assert schema is not None
        assert schema["type"] == "record"
        assert schema["name"] == "SaleRecord"
        assert len(schema["fields"]) == 4

    def test_ensure_schema_creates_file(self, temp_file_storage):
        """Test that _ensure_schema creates schema file."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        exporter._ensure_schema()

        assert exporter.schema_file.exists()

    def test_ensure_schema_reads_existing_file(self, temp_file_storage, tmp_path):
        """Test that _ensure_schema reads existing schema file."""
        custom_schema = {
            "type": "record",
            "name": "CustomSchema",
            "fields": [{"name": "field1", "type": "string"}],
        }

        schema_file = tmp_path / "test_schema.avsc"
        with schema_file.open("w") as f:
            json.dump(custom_schema, f)

        exporter = SalesExporter(
            file_storage=temp_file_storage, schema_file=schema_file
        )
        schema = exporter._ensure_schema()

        assert schema["name"] == "CustomSchema"
        assert len(schema["fields"]) == 1

    def test_ensure_schema_logs_warning_on_creation(self, temp_file_storage):
        """Test that _ensure_schema logs warning when creating default schema."""
        # Remove schema file if it exists to force creation
        exporter = SalesExporter(file_storage=temp_file_storage)
        if exporter.schema_file.exists():
            exporter.schema_file.unlink()

        with patch("src.services.jobs.job1.save_sales.logger") as mock_logger:
            schema = exporter._ensure_schema()
            # Schema should be created
            assert schema is not None
            # Logger warning should be called
            mock_logger.warning.assert_called()


class TestSalesExporterJsonToAvro:
    """Test SalesExporter._json_to_avro method."""

    def test_json_to_avro_creates_avro_file(self, temp_file_storage, sample_sales_data):
        """Test that _json_to_avro creates AVRO file."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        json_path = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        avro_path = exporter._json_to_avro(
            json_path=json_path, for_date=date(2022, 8, 10)
        )

        assert avro_path.exists()
        assert avro_path.suffix == ".avro"
        assert "stg/sales/2022-08-10" in str(avro_path)

    def test_json_to_avro_file_name(self, temp_file_storage, sample_sales_data):
        """Test that _json_to_avro creates file with correct name."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        json_path = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        avro_path = exporter._json_to_avro(
            json_path=json_path, for_date=date(2022, 8, 10)
        )

        assert avro_path.name == "sales_2022-08-10.avro"

    def test_json_to_avro_readable(self, temp_file_storage, sample_sales_data):
        """Test that _json_to_avro creates valid AVRO file."""
        exporter = SalesExporter(file_storage=temp_file_storage)
        json_path = exporter._write_json(
            for_date=date(2022, 8, 10), records=sample_sales_data
        )

        avro_path = exporter._json_to_avro(
            json_path=json_path, for_date=date(2022, 8, 10)
        )

        # Read AVRO file to verify it's valid
        with avro_path.open("rb") as f:
            reader = fastavro.reader(f)
            records = list(reader)
            assert len(records) == 2
            assert records[0]["client"] == "Test Client 1"

    def test_json_to_avro_logs_success(self, temp_file_storage, sample_sales_data):
        """Test that _json_to_avro logs success message."""
        with patch("src.services.jobs.job1.save_sales.logger") as mock_logger:
            exporter = SalesExporter(file_storage=temp_file_storage)
            json_path = exporter._write_json(
                for_date=date(2022, 8, 10), records=sample_sales_data
            )

            exporter._json_to_avro(json_path=json_path, for_date=date(2022, 8, 10))

            # Should log both JSON and AVRO creation
            assert mock_logger.info.call_count >= 1


class TestSaveSalesToLocalDisk:
    """Test save_sales_to_local_disk wrapper function."""

    @patch("src.services.jobs.job1.save_sales.SalesExporter")
    def test_save_sales_to_local_disk_json(self, mock_exporter_class, tmp_path):
        """Test save_sales_to_local_disk for JSON export."""
        mock_exporter = Mock()
        mock_exporter.export.return_value = tmp_path / "test.json"
        mock_exporter_class.return_value = mock_exporter

        result = save_sales_to_local_disk(date_=date(2022, 8, 10), to_stg=False)

        assert result is not None
        assert "test.json" in result
        mock_exporter.export.assert_called_once_with(
            for_date=date(2022, 8, 10), to_stg=False
        )

    @patch("src.services.jobs.job1.save_sales.SalesExporter")
    def test_save_sales_to_local_disk_avro(self, mock_exporter_class, tmp_path):
        """Test save_sales_to_local_disk for AVRO export."""
        mock_exporter = Mock()
        mock_exporter.export.return_value = tmp_path / "test.avro"
        mock_exporter_class.return_value = mock_exporter

        result = save_sales_to_local_disk(date_=date(2022, 8, 10), to_stg=True)

        assert result is not None
        assert "test.avro" in result
        mock_exporter.export.assert_called_once_with(
            for_date=date(2022, 8, 10), to_stg=True
        )

    @patch("src.services.jobs.job1.save_sales.SalesExporter")
    def test_save_sales_to_local_disk_no_data(self, mock_exporter_class):
        """Test save_sales_to_local_disk when no data is found."""
        mock_exporter = Mock()
        mock_exporter.export.return_value = None
        mock_exporter_class.return_value = mock_exporter

        result = save_sales_to_local_disk(date_=date(2022, 8, 10), to_stg=False)

        assert result is None

    @patch("src.services.jobs.job1.save_sales.FILE_STORAGE", "/test/storage")
    @patch("src.services.jobs.job1.save_sales.SalesExporter")
    def test_save_sales_uses_config_file_storage(self, mock_exporter_class):
        """Test that save_sales_to_local_disk uses FILE_STORAGE from config."""
        mock_exporter = Mock()
        mock_exporter.export.return_value = None
        mock_exporter_class.return_value = mock_exporter

        save_sales_to_local_disk(date_=date(2022, 8, 10), to_stg=False)

        # Check that SalesExporter was initialized with correct file_storage
        mock_exporter_class.assert_called_once()
        call_args = mock_exporter_class.call_args
        assert call_args[1]["file_storage"] == "/test/storage"


class TestSalesExporterDefaultSchema:
    """Test SalesExporter default schema."""

    def test_default_schema_structure(self):
        """Test that DEFAULT_SALES_SCHEMA has correct structure."""
        schema = SalesExporter.DEFAULT_SALES_SCHEMA

        assert schema["type"] == "record"
        assert schema["name"] == "SaleRecord"
        assert "fields" in schema

    def test_default_schema_fields(self):
        """Test that DEFAULT_SALES_SCHEMA has all required fields."""
        schema = SalesExporter.DEFAULT_SALES_SCHEMA
        field_names = [field["name"] for field in schema["fields"]]

        assert "client" in field_names
        assert "purchase_date" in field_names
        assert "product" in field_names
        assert "price" in field_names

    def test_default_schema_field_types(self):
        """Test that DEFAULT_SALES_SCHEMA has correct field types."""
        schema = SalesExporter.DEFAULT_SALES_SCHEMA
        fields = {field["name"]: field["type"] for field in schema["fields"]}

        assert fields["client"] == "string"
        assert fields["purchase_date"] == "string"
        assert fields["product"] == "string"
        assert fields["price"] == "double"


class TestSalesExporterIntegration:
    """Integration tests for SalesExporter."""

    def test_full_export_workflow_json(self, temp_file_storage, sample_sales_data):
        """Test full export workflow for JSON."""
        mock_api = Mock()
        mock_api.get_sales.return_value = sample_sales_data

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        # Verify file exists and is readable
        assert result.exists()
        with result.open("r") as f:
            data = json.load(f)
            assert len(data) == 2

    def test_full_export_workflow_avro(self, temp_file_storage, sample_sales_data):
        """Test full export workflow for AVRO."""
        mock_api = Mock()
        mock_api.get_sales.return_value = sample_sales_data

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)
        result = exporter.export(for_date=date(2022, 8, 10), to_stg=True)

        # Verify AVRO file exists and is readable
        assert result.exists()
        with result.open("rb") as f:
            reader = fastavro.reader(f)
            records = list(reader)
            assert len(records) == 2
            assert records[0]["client"] == "Test Client 1"
            assert records[0]["price"] == 100.0

    def test_multiple_exports_same_date(self, temp_file_storage, sample_sales_data):
        """Test that multiple exports to same date overwrite previous files."""
        mock_api = Mock()
        mock_api.get_sales.return_value = sample_sales_data

        exporter = SalesExporter(file_storage=temp_file_storage, api_tool=mock_api)

        # First export
        result1 = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        # Second export with different data
        new_data = [
            {
                "client": "New Client",
                "purchase_date": "2022-08-10",
                "product": "New Product",
                "price": 999.0,
            }
        ]
        mock_api.get_sales.return_value = new_data
        result2 = exporter.export(for_date=date(2022, 8, 10), to_stg=False)

        # Should be same path
        assert result1 == result2

        # Should have new data
        with result2.open("r") as f:
            data = json.load(f)
            assert data[0]["client"] == "New Client"
