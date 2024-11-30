import os
import sqlite3
from datetime import datetime

def init_db():
    """
    Инициализация базы данных
    """
    # Создаем директорию для базы данных, если она не существует
    os.makedirs('/data', exist_ok=True)
    
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sequences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initial_number INTEGER,
            sequence TEXT,
            steps INTEGER,
            calculated_at TIMESTAMP
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
    
    c.execute('''
        INSERT INTO sequences (initial_number, sequence, steps, calculated_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (number, str(sequence), len(sequence)))
    
    conn.commit()
    conn.close()

def get_sequence(number: int) -> list[int]:
    """
    Получение последовательности из базы данных
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    result = c.execute('''
        SELECT sequence FROM sequences 
        WHERE initial_number = ? 
        ORDER BY calculated_at DESC 
        LIMIT 1
    ''', (number,)).fetchone()
    
    conn.close()
    
    if result:
        return eval(result[0])
    return None 

def get_history(sort_by: str = 'date', order: str = 'desc') -> list:
    """
    Получение истории вычислений с сортировкой
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    # Определяем поле для сортировки в SQL
    sort_field = {
        'number': 'initial_number',
        'steps': 'steps',
        'date': 'calculated_at',
        'max_value': 'max_value'
    }.get(sort_by, 'calculated_at')
    
    # Добавляем вычисление максимального значения в запрос
    query = '''
        WITH sequence_stats AS (
            SELECT 
                sequences.id,
                sequences.initial_number,
                sequences.sequence,
                sequences.steps,
                sequences.calculated_at,
                CAST(
                    MAX(
                        CASE 
                            WHEN value != '' AND value != '['  AND value != ']' 
                            THEN CAST(REPLACE(REPLACE(value, ',', ''), ' ', '') AS INTEGER)
                        END
                    ) 
                    OVER (PARTITION BY sequences.id) AS INTEGER
                ) as max_value
            FROM sequences
            CROSS JOIN json_each('[' || REPLACE(REPLACE(sequence, '[', ''), ']', '') || ']')
        )
        SELECT DISTINCT
            initial_number,
            sequence,
            steps,
            calculated_at,
            max_value
        FROM sequence_stats
        ORDER BY {} {}
        LIMIT 100
    '''.format(sort_field, 'DESC' if order == 'desc' else 'ASC')
    
    result = c.execute(query).fetchall()
    conn.close()
    
    return [{
        'number': row[0],
        'sequence': eval(row[1]),
        'steps': row[2],
        'date': datetime.strptime(row[3].split('.')[0], '%Y-%m-%d %H:%M:%S') if row[3] else None,
        'max_value': row[4]
    } for row in result]