from flask import Flask
from statistics import mean  # Добавляем импорт

app = Flask(__name__)

def median(lst):
    """Вычисляет медиану списка"""
    sorted_lst = sorted(lst)
    length = len(sorted_lst)
    if length % 2 == 0:
        return (sorted_lst[length//2 - 1] + sorted_lst[length//2]) / 2
    return sorted_lst[length//2]

def is_even(value):
    """Проверяет, является ли число чётным"""
    try:
        return int(value) % 2 == 0
    except (ValueError, TypeError):
        return False

# Добавляем фильтры в Jinja2
app.jinja_env.globals.update(min=min, max=max)
app.jinja_env.filters['median'] = median
app.jinja_env.filters['even'] = is_even
app.jinja_env.filters['mean'] = mean  # Добавляем фильтр mean

from . import routes
from .database import init_db

# Инициализируем базу данных при запуске
init_db()