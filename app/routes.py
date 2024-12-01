from flask import render_template, request, jsonify, Response
from app import app
from .collatz import calculate_sequence, create_visualization, create_tree_visualization
from .database import save_sequence, get_sequence, get_history, get_next_number, get_min_uncalculated_number
import time

# Глобальная переменная для контроля автоматического расчета
auto_calculate_active = False
current_number = 1

@app.route('/')
def index():
    """Главная страница"""
    # Получаем общее количество записей без ограничения
    result = get_history('steps', 'desc', page=1, per_page=None)
    return render_template('index.html', calculations=result['items'])

@app.route('/history')
def history():
    sort_by = request.args.get('sort', 'date')
    order = request.args.get('order', 'desc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = get_history(sort_by, order, page, per_page)
    
    return render_template('history.html',
                         calculations=result['items'],
                         current_sort=sort_by,
                         current_order=order,
                         pagination=result)

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
    result = get_history('steps', 'desc', page=1, per_page=1000)  # Получаем все расчеты с пагинацией
    return render_template('overview.html', calculations=result['items'])

@app.route('/overview-data')
def overview_data():
    """
    Возвращает данные для визуализации на странице статистики
    """
    result = get_history(sort_by='date', order='desc', per_page=100)
    return jsonify(create_tree_visualization(result['items']))

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

@app.route('/tree/cytoscape')
def tree_cytoscape():
    """Страница с визуализацией через Cytoscape.js"""
    result = get_history('steps', 'desc', page=1, per_page=1000)
    print("Cytoscape view - calculations:", len(result['items']))
    return render_template('tree_cytoscape.html', calculations=result['items'])

@app.route('/tree-data')
def tree_data():
    """API для получения данных дерева"""
    try:
        result = get_history(sort_by='number', order='asc', per_page=500)  # Получаем 500 записей, сортировка по числу по возрастанию
        print("History result:", result)
        
        # Создаем узлы и рёбра
        nodes = []
        edges = []
        seen_nodes = set()
        
        if not result['items']:
            print("No items in result")
            return jsonify({
                'nodes': [],
                'edges': []
            })
        
        print(f"Processing {len(result['items'])} items")
        
        for calc in result['items'][-30:]:  # Берем последние 30 последовательностей
            try:
                sequence = [int(x) for x in calc['sequence']]
                print(f"Processing sequence: {sequence}")
                
                for i, number in enumerate(sequence):
                    if number not in seen_nodes:
                        seen_nodes.add(number)
                        nodes.append({
                            'data': {
                                'id': str(number),  # Преобразуем в строку для совместимости
                                'color': '#FFA500' if number % 2 else '#3388FF',
                                'size': 30 + (len(sequence) - i) * 2
                            }
                        })
                    
                    if i < len(sequence) - 1:
                        edges.append({
                            'data': {
                                'id': f'e{number}-{sequence[i + 1]}',  # Добавляем уникальный id для ребра
                                'source': str(number),
                                'target': str(sequence[i + 1])
                            }
                        })
            except (ValueError, KeyError, TypeError) as e:
                print(f"Error processing sequence: {e}")
                continue
        
        response_data = {
            'nodes': nodes,
            'edges': edges
        }
        print(f"Returning {len(nodes)} nodes and {len(edges)} edges")  # Добавляе логирование
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in tree_data: {e}")
        return jsonify({
            'nodes': [],
            'edges': []
        }), 500 