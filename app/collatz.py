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
    
    fig = go.Figure(data=go.Scatter(
        x=list(range(len(sequence))),
        y=sequence,
        mode='lines+markers',
        name='Последовательность Коллатца'
    ))
    
    fig.update_layout(
        title='Визуализация последовательности Коллатца',
        xaxis_title='Шаг',
        yaxis_title='Значение'
    )
    
    return fig.to_json() 