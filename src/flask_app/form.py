from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import Optional


class DateReport(FlaskForm):
    sale_date = DateField(validators=[Optional()])
    sale_date_stg = DateField(validators=[Optional()])
    submit = SubmitField(label="Отримати звіт")
