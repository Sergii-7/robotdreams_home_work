from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, Optional


class LoginForm(FlaskForm):
    login = StringField(
        label="login",
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "логін"},
    )
    password = PasswordField(
        label="password",
        validators=[InputRequired(), Length(min=8, max=32)],
        render_kw={"placeholder": "пароль"},
    )
    submit = SubmitField("start")


class DateReport(FlaskForm):
    sale_date = DateField(validators=[Optional()])
    sale_date_stg = DateField(validators=[Optional()])
    submit = SubmitField(label="Отримати звіт")
