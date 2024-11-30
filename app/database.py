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
        VALUES (?, ?, ?, ?)
    ''', (number, str(sequence), len(sequence), datetime.now()))
    
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