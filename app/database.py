from datetime import datetime
import pytz
from pymongo import MongoClient, ASCENDING, DESCENDING

# Определяем московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Подключение к MongoDB
client = MongoClient('mongodb://mongodb:27017/')
db = client.collatz
calculations = db.calculations

def init_db():
    """
    Инициализация базы данных
    """
    # Создаем индексы для оптимизации запросов
    calculations.create_index([("number", ASCENDING)])
    calculations.create_index([("date", DESCENDING)])
    calculations.create_index([("steps", ASCENDING)])
    calculations.create_index([("max_value", ASCENDING)])

def save_sequence(number: int, sequence: list[int]):
    """
    Сохранение последовательности в базу данных
    """
    current_time = datetime.now(MOSCOW_TZ)
    
    calculations.insert_one({
        "number": str(number),
        "sequence": sequence,
        "steps": len(sequence) - 1,
        "date": current_time,
        "max_value": str(max(sequence))
    })

def get_sequence(number: int) -> list[int]:
    """
    Получение последовательности из базы данных
    """
    result = calculations.find_one(
        {"number": str(number)},
        sort=[("date", DESCENDING)]
    )
    
    return result["sequence"] if result else None

def get_history(sort_by='date', order='desc', page=1, per_page=10):
    """
    Получение истории вычислений с пагинацией
    """
    # Определяем направление сортировки
    sort_direction = DESCENDING if order.lower() == 'desc' else ASCENDING
    
    # Определяем поле для сортировки
    sort_field = sort_by
    
    # Получаем общее количество записей
    total = calculations.count_documents({})
    
    # Вычисляем смещение для пагинации
    offset = (page - 1) * per_page
    
    # Получаем записи с сортировкой и пагинацией
    cursor = calculations.find({}).sort(sort_field, sort_direction).skip(offset).limit(per_page)
    
    result = list(cursor)  # Преобразуем курсор в список
    
    # Форматируем результат
    return {
        'items': [{
            'number': doc['number'],
            'sequence': doc['sequence'],
            'steps': doc['steps'],
            'date': doc['date'],
            'max_value': doc['max_value']
        } for doc in result],
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page,
        'per_page': per_page
    }

def get_next_number(start_from: int = 1) -> int:
    """
    Получает следующее нерассчитанное число, начиная с start_from
    """
    while True:
        result = calculations.find_one({"number": str(start_from)})
        if not result:
            return start_from
        start_from += 1

def get_min_uncalculated_number() -> int:
    """
    Находит минимальное нерассчитанное число
    """
    # Получаем все числа из базы, сортируем как числа
    cursor = calculations.find({}, {"number": 1}).sort("number", ASCENDING)
    numbers = [int(doc["number"]) for doc in cursor]
    
    if not numbers:
        return 1
        
    # Ищем первый пропуск в последовательности
    for i in range(len(numbers)):
        if i + 1 != numbers[i]:
            return i + 1
            
    # Если пропусков нет, возвращаем следующее число
    return len(numbers) + 1