from flask import Flask

from src.config import STATIC_FOLDER, TEMPLATE_FOLDER

app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER,  # Вказуємо шлях до папки templates
    static_folder=STATIC_FOLDER,  # Вказуємо шлях до папки static
)
