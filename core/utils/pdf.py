from typing import Optional

import fpdf
from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT
STATIC_ROOT = settings.STATIC_ROOT or settings.STATICFILES_DIRS[0]


class PDF(fpdf.FPDF):

    def __init__(self, *args, test, tg_user_id, company_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.test = test
        self.tg_user_id = tg_user_id
        self.company_id = company_id
        self.add_font(
            "Noto_Serif", style="", fname=f"{STATIC_ROOT}/fonts/NotoSerif-Regular.ttf")
        self.add_font(
            "Noto_Serif", style="B", fname=f"{STATIC_ROOT}/fonts/NotoSerif-Bold.ttf")
        self.add_font(
            "Noto_Serif", style="I", fname=f"{STATIC_ROOT}/fonts/NotoSerif-Italic.ttf")
        self.add_font(
            "Noto_Serif", style="BI", fname=f"{STATIC_ROOT}/fonts/NotoSerif-BoldItalic.ttf")

    # def header(self):
    def document_title(self):
        # Rendering logo:

        self.set_font("Noto_Serif", "B", 15)
        width = self.get_string_width(self.title) + 6
        self.set_x((210 - width) / 2)
        # self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        # self.set_text_color(220, 50, 50)
        self.set_line_width(1)
        self.cell(
            width,
            9,
            self.title,
            # border=1,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            fill=True,
        )
        # self.set_text_color()

    def footer(self):
        self.set_y(-15)
        self.set_font("Noto_Serif", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def get_filename(
            self, graph: bool = False, statistics: bool = False, pdf: bool = False) -> str:
        """Возвращает путь к файлу"""
        filename = ''

        if self.tg_user_id:
            directory = 'users_tests_graphs'
            filename = f'{directory}/tg_user_id:{self.tg_user_id}_seven_petals'
        elif self.company_id:
            directory = 'companies_tests_graphs'
            filename = f'{directory}/company_id:{self.company_id}_seven_petals'

        if filename:
            if graph:
                filename += f'_id:{self.test.pk}.png'
            elif statistics:
                filename += '_statistics.png'
            elif pdf:
                filename += '.pdf'

        return filename

    def print_graphs(self):
        """Вывод графиков в pdf"""
        if graph_filename := self.get_filename(graph=True):
            self.image(f'{MEDIA_ROOT}/{graph_filename}', 10, 20, 100, title="График")
        if statistics_filename := self.get_filename(statistics=True):
            self.image(f'{MEDIA_ROOT}/{statistics_filename}', 100, 30, 80, title="Статистика")

    def chapter_title(self, num, label):
        self.set_font("Noto_Serif", "", 12)
        self.set_fill_color(200, 220, 255)
        self.cell(
            0,
            6,
            f"Chapter {num} : {label}",
            new_x="LMARGIN",
            new_y="NEXT",
            border="L",
            fill=True,
        )
        self.ln(4)

    def chapter_body(self, text):
        with self.text_columns(
                ncols=1, gutter=10, text_align="J", line_height=1.19
        ) as cols:
            self.set_font("Noto_Serif", "", size=12)
            cols.write(text)
            cols.ln()

            # Final mention in italics:
            # self.set_font(style="I")
            # cols.write("(end of excerpt)")

    def print_chapter(self, num, title, text):
        self.add_page()
        self.document_title()
        # self.chapter_title(num, title)
        self.print_graphs()
        self.ln(130)
        self.chapter_body(text)


# Instantiation of inherited class
def create_pdf(test, tg_user_id: Optional[int] = None, company_id: Optional[int] = None) -> str:
    """Для создания PDF файлов"""
    pdf = PDF(test=test, tg_user_id=tg_user_id, company_id=company_id)
    pdf.set_title("Результаты исследования 'Семь лепестков'")
    # pdf.set_author("Пользователь такой-то")
    pdf.print_chapter(num=1, title="Результаты исследования", text=test.presentation_data())
    # pdf.print_chapter(num=1, title="I think, they", text=test)

    path = f'{MEDIA_ROOT}/{pdf.get_filename(pdf=True)}'
    pdf.output()
    return path
