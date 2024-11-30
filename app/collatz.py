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