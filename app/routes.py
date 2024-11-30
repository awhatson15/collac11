from flask import render_template, request, jsonify
from app import app
from .collatz import calculate_sequence, create_visualization, create_overview_visualization
from .database import save_sequence, get_sequence, get_history

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    sort_by = request.args.get('sort', 'date')  # По умолчанию сортируем по дате
    order = request.args.get('order', 'desc')  # По умолчанию в обратном порядке
    calculations = get_history(sort_by, order)
    return render_template('history.html', 
                         calculations=calculations, 
                         current_sort=sort_by, 
                         current_order=order)

@app.route('/calculate', methods=['POST'])
def calculate():
    number = int(request.form['number'])
    
    # Проверяем, есть ли последовательность в базе
    cached_sequence = get_sequence(number)
    if cached_sequence:
        visualization = create_visualization(cached_sequence)
        return jsonify({
            'sequence': cached_sequence,
            'visualization': visualization,
            'cached': True
        })
    
    # Вычисляем новую последовательность
    sequence = calculate_sequence(number)
    save_sequence(number, sequence)
    visualization = create_visualization(sequence)
    
    return jsonify({
        'sequence': sequence,
        'visualization': visualization,
        'cached': False
    })

@app.route('/overview')
def overview():
    """Страница с общей визуализацией"""
    calculations = get_history('steps', 'desc')  # Получаем все расчеты
    return render_template('overview.html', calculations=calculations)

@app.route('/overview-data')
def overview_data():
    """API для получения данных визуализации"""
    calculations = get_history('steps', 'desc')
    
    visualization = create_overview_visualization([{
        'number': calc['number'],
        'steps': calc['steps'],
        'max_value': calc['max_value']
    } for calc in calculations])
    
    return jsonify(visualization) 