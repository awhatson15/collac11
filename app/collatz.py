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
    Создает расширенную визуализацию статистики
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
    from collections import Counter
    
    # Создаем сетку графиков 3x2
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Распределение количества шагов',
            'Корреляция шагов и максимального значения',
            'Распределение максимальных значений',
            'Тепловая карта первых шагов',
            'История вычислений',
            'Распределение чётных/нечётных чисел'
        ),
        specs=[[{"type": "histogram"}, {"type": "scatter"}],
               [{"type": "histogram"}, {"type": "heatmap"}],
               [{"type": "scatter"}, {"type": "pie"}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # 1. Гистограмма распределения шагов
    fig.add_trace(
        go.Histogram(
            x=[calc['steps'] for calc in calculations],
            name='Распределение шагов',
            nbinsx=30,
            marker_color='rgba(44, 160, 44, 0.7)',
            hovertemplate='Шагов: %{x}<br>Количество: %{y}<extra></extra>'
        ),
        row=1, col=1
    )

    # 2. Корреляция шагов и максимального значения
    fig.add_trace(
        go.Scatter(
            x=[calc['steps'] for calc in calculations],
            y=[int(calc['max_value']) for calc in calculations],
            mode='markers',
            name='Корреляция',
            marker=dict(
                size=8,
                color=[int(calc['number']) for calc in calculations],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Начальное число")
            ),
            hovertemplate='Шагов: %{x}<br>Макс. значение: %{y}<br>Число: %{marker.color}<extra></extra>'
        ),
        row=1, col=2
    )

    # 3. Гистограмма максимальных значений
    fig.add_trace(
        go.Histogram(
            x=[int(calc['max_value']) for calc in calculations],
            name='Макс. значения',
            nbinsx=30,
            marker_color='rgba(31, 119, 180, 0.7)',
            hovertemplate='Макс. значение: %{x}<br>Количество: %{y}<extra></extra>'
        ),
        row=2, col=1
    )

    # 4. Тепловая карта первых шагов
    first_steps = []
    for calc in calculations:
        seq = calc['sequence'][:min(10, len(calc['sequence']))]  # Берем первые 10 шагов
        first_steps.append(seq + [None] * (10 - len(seq)))  # Дополняем None если шагов меньше 10
    
    first_steps_array = np.array(first_steps)
    fig.add_trace(
        go.Heatmap(
            z=first_steps_array.T,
            x=[calc['number'] for calc in calculations[-50:]],  # Последние 50 чисел
            y=[f'Шаг {i+1}' for i in range(10)],
            colorscale='Viridis',
            hovertemplate='Число: %{x}<br>%{y}: %{z}<extra></extra>'
        ),
        row=2, col=2
    )

    # 5. График истории вычислений
    fig.add_trace(
        go.Scatter(
            x=[calc['date'] for calc in calculations],
            y=[int(calc['number']) for calc in calculations],
            mode='lines+markers',
            name='История',
            line=dict(width=1),
            marker=dict(size=6),
            hovertemplate='Дата: %{x}<br>Число: %{y}<extra></extra>'
        ),
        row=3, col=1
    )

    # 6. Круговая диаграмма чётных/нечётных
    even_odd = Counter([int(calc['number']) % 2 for calc in calculations])
    fig.add_trace(
        go.Pie(
            labels=['Чётные', 'Нечётные'],
            values=[even_odd[0], even_odd[1]],
            marker=dict(colors=['rgba(44, 160, 44, 0.7)', 'rgba(214, 39, 40, 0.7)']),
            hovertemplate='%{label}<br>Количество: %{value}<br>Процент: %{percent}<extra></extra>'
        ),
        row=3, col=2
    )

    # Настройка макета
    fig.update_layout(
        height=1500,
        showlegend=False,
        title_text=f"Расширенная статистика по {len(calculations)} числам",
        title_x=0.5,
        title_font=dict(size=24),
        template='plotly_white'
    )

    # Настройка осей и подписей
    fig.update_xaxes(title_text="Количество шагов", row=1, col=1)
    fig.update_yaxes(title_text="Количество чисел", row=1, col=1)

    fig.update_xaxes(title_text="Количество шагов", row=1, col=2)
    fig.update_yaxes(title_text="Максимальное значение", row=1, col=2)

    fig.update_xaxes(title_text="Максимальное значение", row=2, col=1)
    fig.update_yaxes(title_text="Количество чисел", row=2, col=1)

    fig.update_xaxes(title_text="Начальное число", row=2, col=2)
    
    fig.update_xaxes(title_text="Дата", row=3, col=1)
    fig.update_yaxes(title_text="Начальное число", row=3, col=1)

    return fig.to_json() 

def create_tree_visualization(calculations: list) -> dict:
    """
    Создает визуализацию последовательностей в виде дерева
    """
    import plotly.graph_objects as go
    import networkx as nx
    
    # Создаем направленный граф
    G = nx.DiGraph()
    
    # Добавляем узлы и рёбра из всех последовательностей
    for calc in calculations[-15:]:  # Берем последние 15 последовательностей
        sequence = [int(x) for x in calc['sequence']]
        for i in range(len(sequence) - 1):
            G.add_edge(sequence[i], sequence[i + 1])
    
    # Используем иерархический layout
    pos = nx.spring_layout(G, k=2)
    
    # Корректируем y-координаты на основе расстояния до конечного узла (1)
    # Находим все пути до 1
    paths_to_one = []
    for node in G.nodes():
        try:
            path = nx.shortest_path(G, node, 1)
            paths_to_one.append((node, len(path)))
        except nx.NetworkXNoPath:
            continue
    
    # Нормализуем y-координаты на основе длины пути
    max_path_length = max(length for _, length in paths_to_one) if paths_to_one else 1
    for node, path_length in paths_to_one:
        x, y = pos[node]
        # Инвертируем y-координату, чтобы большие числа были сверху
        pos[node] = (x, 1 - (path_length - 1) / max_path_length)
    
    # Корректируем x-координаты для узлов с одинаковой y-координатой
    y_levels = {}
    for node in G.nodes():
        if node in pos:
            y = round(pos[node][1], 3)
            if y not in y_levels:
                y_levels[y] = []
            y_levels[y].append(node)
    
    # Равномерно распределяем узлы на каждом уровне
    for y, nodes in y_levels.items():
        sorted_nodes = sorted(nodes)
        width = 1.0 / (len(nodes) + 1)
        for i, node in enumerate(sorted_nodes):
            x = (i + 1) * width
            pos[node] = (x, y)
    
    # Создаем списки для узлов
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    # Заполняем списки координатами и значениями узлов
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))
        # Нечетные числа выделяем оранжевым цветом
        node_color.append('#FFA500' if node % 2 else '#3388FF')
        # Размер узла зависит от количества связей
        node_size.append(30 + len(list(G.neighbors(node))) * 5)
    
    # Создаем списки для рёбер
    edge_x = []
    edge_y = []
    
    # Заполняем списки координатами рёбер
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        # Добавляем промежуточную точку для создания изогнутых линий
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        edge_x.extend([x0, mid_x, x1, None])
        edge_y.extend([y0, mid_y, y1, None])
    
    # Создаем линии рёбер
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    
    # Создаем узлы
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=1, color='#888')
        ),
        showlegend=False
    )
    
    # Создаем фигуру
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-0.1, 1.1]
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-0.1, 1.1]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            autosize=True
        )
    )
    
    return fig.to_dict() 