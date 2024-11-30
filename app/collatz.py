def calculate_sequence(n: int) -> list[int]:
    """
    Вычисляет последовательность Коллатца для заданного числа
    """
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def create_visualization(sequence: list[int]) -> dict:
    """
    Создает данные для визуализации с помощью Plotly
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Создаем график с двумя подграфиками
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Последовательность Коллатца', 'Количество шагов'),
        row_heights=[0.7, 0.3],
        vertical_spacing=0.15
    )
    
    # График последовательности
    fig.add_trace(
        go.Scatter(
            x=list(range(len(sequence))),
            y=sequence,
            mode='lines+markers',
            name='Значения'
        ),
        row=1, col=1
    )
    
    # График шагов (накопительный)
    steps = list(range(len(sequence)))
    fig.add_trace(
        go.Bar(
            x=steps,
            y=[1] * len(steps),  # Каждый шаг имеет высоту 1
            name='Шаги',
            marker_color='rgba(55, 128, 191, 0.7)',
            hovertemplate='Шаг %{x}<br>Всего шагов: %{customdata}<extra></extra>',
            customdata=[[i+1] for i in steps]
        ),
        row=2, col=1
    )
    
    # Настройка макета
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text=f"Визуализация последовательности Коллатца (всего шагов: {len(sequence)-1})"
    )
    
    # Настройка осей
    fig.update_xaxes(title_text="Шаг", row=1, col=1)
    fig.update_yaxes(title_text="Значение", row=1, col=1)
    fig.update_xaxes(title_text="Шаг", row=2, col=1)
    fig.update_yaxes(title_text="", row=2, col=1)
    
    return fig.to_json() 

def create_overview_visualization(calculations: list) -> dict:
    """
    Создает общую визуализацию всех расчетов
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Сортируем данные по количеству шагов
    calculations.sort(key=lambda x: x['steps'])
    
    # Создаем график с тремя подграфиками
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Количество шагов для каждого числа',
            'Максимальные значения',
            'Корреляция между начальным числом и количеством шагов'
        ),
        row_heights=[0.33, 0.33, 0.33],
        vertical_spacing=0.1
    )
    
    # График количества шагов
    fig.add_trace(
        go.Bar(
            x=[calc['number'] for calc in calculations],
            y=[calc['steps'] for calc in calculations],
            name='Количество шагов',
            marker_color='rgba(55, 128, 191, 0.7)',
            hovertemplate='Число: %{x}<br>Шагов: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # График максимальных значений
    fig.add_trace(
        go.Scatter(
            x=[calc['number'] for calc in calculations],
            y=[calc['max_value'] for calc in calculations],
            mode='markers',
            name='Максимальные значения',
            marker=dict(
                size=8,
                color='rgba(255, 65, 54, 0.7)',
            ),
            hovertemplate='Число: %{x}<br>Макс. значение: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # График корреляции
    fig.add_trace(
        go.Scatter(
            x=[calc['number'] for calc in calculations],
            y=[calc['steps'] for calc in calculations],
            mode='markers',
            name='Корреляция',
            marker=dict(
                size=8,
                color='rgba(44, 160, 44, 0.7)',
            ),
            hovertemplate='Число: %{x}<br>Шагов: %{y}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Настройка макета
    fig.update_layout(
        height=1200,
        showlegend=True,
        title_text=f"Общая статистика по {len(calculations)} числам"
    )
    
    # Настройка осей
    fig.update_xaxes(title_text="Начальное число", row=1, col=1)
    fig.update_yaxes(title_text="Количество шагов", row=1, col=1)
    
    fig.update_xaxes(title_text="Начальное число", row=2, col=1)
    fig.update_yaxes(title_text="Максимальное значение", row=2, col=1)
    
    fig.update_xaxes(title_text="Начальное число", row=3, col=1)
    fig.update_yaxes(title_text="Количество шагов", row=3, col=1)
    
    return fig.to_json() 