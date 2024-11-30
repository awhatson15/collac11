from flask import Flask

app = Flask(__name__)

from . import routes
from .database import init_db

# Инициализируем базу данных при запуске
init_db()