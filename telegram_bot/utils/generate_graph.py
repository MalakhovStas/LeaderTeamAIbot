"""Модуль инструментов для генерации графиков"""

import numpy
from aiogram.types import InputFile
from django.conf import settings
from matplotlib import pyplot

from psychological_testing.models import SevenPetals


async def delete_prev_message_and_send_graph(tg_user_id, graph_filename):
    """Удаляет последнее сообщение от бота пользователю и отправляет ему график"""
    from ..loader import bot, Base
    from telegram_bot.handlers.handlers import delete_message

    if last_message_id := await Base.button_search_and_action_any_collections(
            user_id=tg_user_id, action='get',
            button_name='last_handler_sent_message_id', updates_data=True):
        await delete_message(chat_id=tg_user_id, message_id=last_message_id)
    await bot.send_photo(chat_id=tg_user_id, photo=InputFile(graph_filename))


async def seven_petals_generate_graph(tg_user_id, seven_petals: SevenPetals):
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
    filename = settings.MEDIA_ROOT + f'/tg_id:{tg_user_id}_seven_petals_graph.png'
    pyplot.savefig(filename)
    pyplot.close()
    await delete_prev_message_and_send_graph(tg_user_id=tg_user_id, graph_filename=filename)
