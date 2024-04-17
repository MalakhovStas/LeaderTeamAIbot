from django.db import models
from django.db.models import Case, Value, When, BooleanField
from django.utils import timezone


# class CalendarEventsQuerySet(models.query.QuerySet):
#     """Класс для переопределения запросов к БД для модели CalendarEvents"""
#
#     @staticmethod
#     def check_active_logic(obj):
#         """Метод проверки активности и изменения поля is_active при запросе"""
#         if active := timezone.now() >= obj.event_date:
#             obj.is_active = active
#             obj.save()
#
#     def active(self):
#         """Фильтр возвращает только активные события на момент запроса."""
#         return self.filter(event_date__lte=timezone.now(), is_active=True)
#
#     def all(self):
#         """Переопределение метода all"""
#         objects = super().all()
#         print('hello world ALL')
#         print(objects)
#         # for obj in objects:
#         #     self.check_active_logic(obj)
#         return objects
#
#     def get(self, **kwargs):
#         """Переопределение метода get"""
#         obj = super().get(**kwargs)
#         print('hello world GET')
#         print(obj)
#         # self.check_active_logic(obj)
#         return obj
#
#     def first(self):
#         """Переопределение метода first"""
#         obj = super().first()
#         print('hello world FIRST')
#         print(obj)
#         # self.check_active_logic(obj)
#         return obj


# class CalendarEventsManager(models.Manager.from_queryset(CalendarEventsQuerySet)):

class CalendarEventManager(models.Manager):
    """Переопределение менеджера для работы с моделью CalendarEvent"""

    def get_queryset(self):
        """Добавляет динамическое поле 'is_active' к каждому объекту в QuerySet"""
        return super().get_queryset().annotate(
            active_event=Case(
                When(event_date__gte=timezone.now(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
