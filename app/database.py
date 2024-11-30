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

def get_history() -> list:
    """
    Получение истории вычислений
    """
    conn = sqlite3.connect('/data/collatz.db')
    c = conn.cursor()
    
    result = c.execute('''
        SELECT initial_number, sequence, steps, calculated_at 
        FROM sequences 
        ORDER BY calculated_at DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    return [{
        'number': row[0],
        'sequence': eval(row[1]),
        'steps': row[2],
        'date': datetime.strptime(row[3].split('.')[0], '%Y-%m-%d %H:%M:%S') if row[3] else None
    } for row in result]