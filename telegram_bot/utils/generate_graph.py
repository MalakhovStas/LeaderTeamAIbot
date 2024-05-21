"""Модуль инструментов для генерации графиков"""
from typing import Optional

import numpy
from django.conf import settings
from matplotlib import pyplot

from psychological_testing.models import SevenPetals
from utils.utils import check_or_create_directory


def seven_petals_generate_graph(
        seven_petals: SevenPetals,
        tg_user_id: Optional[int] = None,
        company_id: Optional[int] = None
) -> Optional[str]:
    """Функция для генерации, сохранения и отправки пользователю
    графика на основе опроса 'Семь лепестков'"""

    if tg_user_id:
        directory = 'users_tests_graphs'
        filename = f'{directory}/tg_user_id:{tg_user_id}_seven_petals_id:{seven_petals.pk}.png'
    elif company_id:
        directory = 'companies_tests_graphs'
        filename = f'{directory}/company_id:{company_id}_seven_petals_id:{seven_petals.pk}.png'
    else:
        directory = None
        filename = None

    if directory and filename and check_or_create_directory(f'{settings.MEDIA_ROOT}/{directory}'):
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
        pyplot.savefig(f'{settings.MEDIA_ROOT}/{filename}')
        pyplot.close()
    return filename


def seven_petals_generate_graph_statistics(
        all_seven_petals: list[SevenPetals],
        tg_user_id: Optional[int] = None,
        company_id: Optional[int] = None
) -> Optional[str]:
    """Функция для генерации, сохранения и отправки пользователю графика статистики изменения
    результатов тестирования на основе всех опросов 'Семь лепестков'"""

    if tg_user_id:
        directory = 'users_tests_graphs'
        filename = f'{directory}/tg_user_id:{tg_user_id}_seven_petals_statistics.png'
    elif company_id:
        directory = 'companies_tests_graphs'
        filename = f'{directory}/company_id:{company_id}_seven_petals_statistics.png'
    else:
        directory = None
        filename = None

    if directory and filename and check_or_create_directory(f'{settings.MEDIA_ROOT}/{directory}'):
        x_labels = ['Оптимизм', 'Поток', 'Смысл', 'Любить', 'Играть', 'Влиять']
        fig, axs = pyplot.subplots(nrows=7, ncols=1, sharex=True, sharey=True, figsize=(8, 15))
        pyplot.xticks(numpy.arange(0, len(all_seven_petals), step=1))
        pyplot.yticks(numpy.arange(-10, 11, step=1))
        # axs = np.ravel(axs)
        # axs.xaxis.set_major_formatter(FuncFormatter(formatX))
        # fig.suptitle('Статистика тестирования')
        pyplot.subplots_adjust(top=0.855, bottom=0.15)

        fig.tight_layout(h_pad=2)
        optimism = []
        stream = []
        sense = []
        love = []
        play = []
        study = []
        impact = []
        for test in all_seven_petals:
            optimism.append(test.optimism)
            stream.append(test.stream)
            sense.append(test.sense)
            love.append(test.love)
            play.append(test.play)
            study.append(test.study)
            impact.append(test.impact)

        # axs[0].plot(opti, label='Оптимизм', color='#15B01A', marker='o')  # построение графика с подписью
        axs[0].plot(optimism, color='g', marker='o')
        axs[0].set_title('Оптимизм')

        # axs[1].plot(potok, label='Поток', color='#069AF3', marker='o')  # построение графика с подписью
        axs[1].plot(stream, color='c', marker='o')
        axs[1].set_title('Поток')

        # axs[2].plot(smisl, label='Смысл', color='#A52A2A', marker='o')  # построение графика с подписью
        axs[2].plot(sense, color='m', marker='o')
        axs[2].set_title('Смысл')

        # axs[3].plot(lubit, label='Любить', color='#FFD700', marker='o')  # построение графика с подписью
        axs[3].plot(love, color='y', marker='o')
        axs[3].set_title('Любить')

        # axs[4].plot(igrat, label='Играть', color='#0000FF', marker='o')  # построение графика с подписью
        axs[4].plot(play, color='b', marker='o')
        axs[4].set_title('Играть')

        # axs[5].plot(vliyat, label='Влиять', color='#FF4500', marker='o')  # построение графика с подписью
        axs[5].plot(impact, color='r', marker='o')
        axs[5].set_title('Влиять')

        axs[6].plot(study, color='g', marker='o')
        axs[6].set_title('Учиться')


        # plt.xlabel('Количество словарей')  # подпись оси x
        # plt.ylabel('Значения')  # подпись оси y
        # plt.title('График данных')  # заголовок графика
        # plt.legend()  # добавление легенды

        # plt.show()  # отображение графика

        pyplot.savefig(f'{settings.MEDIA_ROOT}/{filename}')
        pyplot.close()

    return filename
