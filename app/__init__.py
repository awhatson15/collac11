from flask import Flask

app = Flask(__name__)

# Добавляем фильтры min и max в Jinja2
app.jinja_env.globals.update(min=min, max=max)

from . import routes
from .database import init_db

# Инициализируем базу данных при запуске
init_db()