import os
import sqlite3
from datetime import datetime
import pytz

# Определяем московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def init_db():
    """
    Инициализация базы данных
    """
    # Создаем директорию для базы данных, если она не существует
    os.makedirs('/data', exist_ok=True)
    
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    # Создаем таблицу calculations с измененным типом для number и max_value
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            sequence TEXT,
            steps INTEGER,
            date TIMESTAMP,
            max_value TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_sequence(number: int, sequence: list[int]):
    """
    Сохранение последовательности в базу данных
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    # Получаем текущее время в московском часовом поясе
    current_time = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
    
    c.execute('''
        INSERT INTO calculations (number, sequence, steps, date, max_value)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        str(number),
        str(sequence),
        len(sequence) - 1,
        current_time.strftime('%Y-%m-%d %H:%M:%S'),
        str(max(sequence))
    ))
    
    conn.commit()
    conn.close()

def get_sequence(number: int) -> list[int]:
    """
    Получение последовательности из базы данных
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    result = c.execute('''
        SELECT sequence FROM calculations 
        WHERE CAST(number AS TEXT) = ? 
        ORDER BY date DESC 
        LIMIT 1
    ''', (str(number),)).fetchone()
    
    conn.close()
    
    if result:
        return eval(result[0])
    return None

def get_history(sort_by='date', order='desc'):
    """
    Получение истории вычислений
    """
    conn = sqlite3.connect('/data/collatz.db')
    cursor = conn.cursor()
    
    # Определяем порядок сортировки
    order = order.upper()
    if order not in ['ASC', 'DESC']:
        order = 'DESC'
    
    # Определяем оле для сортировки с учетом типа max_value
    sort_columns = {
        'number': 'CAST(number AS INTEGER)',
        'steps': 'CAST(steps AS INTEGER)',
        'max_value': 'CAST(max_value AS INTEGER)',
        'date': 'date'
    }
    sort_column = sort_columns.get(sort_by, 'date')
    
    cursor.execute(f'''
        SELECT number, sequence, steps, date, max_value 
        FROM calculations 
        ORDER BY {sort_column} {order}
    ''')
    
    result = cursor.fetchall()
    conn.close()
    
    return [{
        'number': row[0],
        'sequence': eval(row[1]),
        'steps': row[2],
        'date': datetime.strptime(row[3].split('.')[0], '%Y-%m-%d %H:%M:%S') if row[3] else None,
        'max_value': int(row[4])
    } for row in result]

def get_next_number(start_from: int = 1) -> int:
    """
    Получает следующее нерассчитанное число, начиная с start_from
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    while True:
        result = c.execute('''
            SELECT 1 FROM calculations 
            WHERE CAST(number AS INTEGER) = ?
        ''', (start_from,)).fetchone()
        
        if not result:
            conn.close()
            return start_from
        start_from += 1

def get_min_uncalculated_number() -> int:
    """
    Находит минимальное нерассчитанное число
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    # Получаем все числа из базы, сортируем как числа, а не строки
    result = c.execute('''
        SELECT CAST(number AS INTEGER) as num 
        FROM calculations 
        ORDER BY num ASC
    ''').fetchall()
    
    conn.close()
    
    if not result:
        return 1
        
    numbers = [row[0] for row in result]
    
    # Ищем первый пропуск в последовательности
    for i in range(len(numbers)):
        if i + 1 != numbers[i]:
            return i + 1
            
    # Если пропусков нет, возвращаем следующее число
    return len(numbers) + 1