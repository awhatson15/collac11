from flask import render_template, request, jsonify, Response
from app import app
from .collatz import calculate_sequence, create_visualization, create_overview_visualization
from .database import save_sequence, get_sequence, get_history, get_next_number, get_min_uncalculated_number
import time

# Глобальная переменная для контроля автоматического расчета
auto_calculate_active = False
current_number = 1

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

@app.route('/auto-calculate/start')
def start_auto_calculate():
    """Запуск автоматического расчета"""
    global auto_calculate_active, current_number
    auto_calculate_active = True
    # Используем минимальное нерассчитанное число, если не указано начальное
    start_from = request.args.get('start_from')
    current_number = int(start_from) if start_from else get_min_uncalculated_number()
    return jsonify({'status': 'started', 'from': current_number})

@app.route('/auto-calculate/stop')
def stop_auto_calculate():
    """Остановка автоматического расчета"""
    global auto_calculate_active
    auto_calculate_active = False
    return jsonify({'status': 'stopped'})

@app.route('/auto-calculate/status')
def auto_calculate_status():
    """Получение статуса автоматического расчета"""
    return jsonify({
        'active': auto_calculate_active,
        'current_number': current_number
    })

@app.route('/auto-calculate/stream')
def auto_calculate_stream():
    """Поток событий для автоматического расчета"""
    def generate():
        global current_number
        while True:
            if not auto_calculate_active:
                yield 'data: {"status": "stopped"}\n\n'
                break
                
            next_number = get_next_number(current_number)
            sequence = calculate_sequence(next_number)
            save_sequence(next_number, sequence)
            
            yield f'data: {{"number": {next_number}, "steps": {len(sequence)-1}}}\n\n'
            
            current_number = next_number + 1
            time.sleep(1)  # Пауза между расчетами
            
    return Response(generate(), mimetype='text/event-stream') 