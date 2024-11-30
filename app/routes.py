from flask import render_template, request, jsonify
from app import app
from .collatz import calculate_sequence, create_visualization
from .database import save_sequence, get_sequence, get_history

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    calculations = get_history()
    return render_template('history.html', calculations=calculations, max=max)

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