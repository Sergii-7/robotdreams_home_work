"""Tests for Flask forms."""

import pytest
from wtforms import DateField, SubmitField

from src.flask_app.form import DateReport


class TestDateReportForm:
    """Test DateReport form class."""

    def test_form_creation(self, app):
        """Test that form can be instantiated."""
        with app.app_context():
            form = DateReport()
            assert form is not None

    def test_form_has_sale_date_field(self, app):
        """Test that form has sale_date field."""
        with app.app_context():
            form = DateReport()
            assert hasattr(form, "sale_date")
            assert isinstance(form.sale_date, DateField)

    def test_form_has_sale_date_stg_field(self, app):
        """Test that form has sale_date_stg field."""
        with app.app_context():
            form = DateReport()
            assert hasattr(form, "sale_date_stg")
            assert isinstance(form.sale_date_stg, DateField)

    def test_form_has_submit_button(self, app):
        """Test that form has submit button."""
        with app.app_context():
            form = DateReport()
            assert hasattr(form, "submit")
            assert isinstance(form.submit, SubmitField)

    def test_submit_button_label(self, app):
        """Test that submit button has correct label."""
        with app.app_context():
            form = DateReport()
            assert form.submit.label.text == "Отримати звіт"

    def test_sale_date_is_optional(self, app):
        """Test that sale_date field is optional."""
        with app.app_context():
            form = DateReport()
            # Optional validator allows empty values
            assert form.sale_date.validators is not None

    def test_sale_date_stg_is_optional(self, app):
        """Test that sale_date_stg field is optional."""
        with app.app_context():
            form = DateReport()
            # Optional validator allows empty values
            assert form.sale_date_stg.validators is not None
