"""Модуль инструментов для генерации графиков"""

import numpy
from django.conf import settings
from matplotlib import pyplot

from psychological_testing.models import SevenPetals


async def seven_petals_generate_graph(tg_user_id: int, seven_petals: SevenPetals) -> str:
    """Функция для генерации, сохранения и отправки пользователю
    графика на основе опроса 'Семь лепестков'"""

    # Количество вершин и их значения
    num_vertices = 6
    vertex_names = [
        'Оптимизм',
        'Поток',
        'Смысл',
        'Любить',
        'Играть',
        'Влиять'
    ]

    # Установление значений вершин
    vertex_values = [seven_petals.optimism, seven_petals.stream, seven_petals.sense,
                     seven_petals.love, seven_petals.play, seven_petals.impact]

    # Углы для вершин многоугольника
    angles = numpy.linspace(0, 2 * numpy.pi, num_vertices, endpoint=False).tolist()
    angles += angles[:1]

    # Удаление случайных значений радиусов, используйте переданные значения
    radii = vertex_values
    radii += radii[:1]

    fig, ax = pyplot.subplots(subplot_kw={'projection': 'polar'})

    # Редактирование кода для создания правильного графика
    ax.plot(angles, radii, color='skyblue', linewidth=1, linestyle='solid')
    ax.fill(angles, radii, color='skyblue', alpha=0.6)

    # Добавление названий вершин на график
    for i in range(num_vertices):
        ax.text(angles[i], radii[i], f' {vertex_names[i]} ({vertex_values[i]})', fontsize=12,
                ha='right', va='bottom')

    # Удаление значений углов (градусов) и меток радиусов
    # ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Сохранение и отправка графика
    filename = f'users_tests_graphs/tg_id:{tg_user_id}_seven_petals_graph.png'
    pyplot.savefig(f'{settings.MEDIA_ROOT}/{filename}')
    pyplot.close()
    return filename
