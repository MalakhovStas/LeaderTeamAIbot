"""Модуль формирования моделей БД психологического тестирования пользователя"""
import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class SevenPetals(BaseModel):
    """Модель хранения данных опроса 'Семь лепестков'"""

    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='seven_petals_user',
        verbose_name=_('user'))

    company = models.ForeignKey(
        to='company.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='seven_petals_company',
        verbose_name=_('company'))

    optimism = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('optimism'))

    stream = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('stream'))

    sense = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('sense'))

    love = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('love'))

    play = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('play'))

    study = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('study'))

    impact = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('impact'))

    general_questions = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('general questions'))

    open_questions_pleasure = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions pleasure'))

    open_questions_irritation = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions irritation'))

    graph = models.ImageField(
        upload_to='users_tests_graphs/', null=True, blank=True, verbose_name=_('graph'))

    ai_recommendations = models.TextField(
        null=True, blank=True, verbose_name=_('AI recommendations'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('seven petals')
        verbose_name_plural = _('seven petals')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.company and not self.user and not self.graph:
            from telegram_bot.utils.generate_graph import (
                seven_petals_generate_graph,
                seven_petals_generate_graph_statistics
            )
            self.graph = seven_petals_generate_graph(
                seven_petals=self,
                company_id=self.company.pk
            )
            seven_petals_generate_graph_statistics(
                all_seven_petals=SevenPetals.objects.filter(company=self.company).all(),
                company_id=self.company.pk
            )
            super().save(*args, **kwargs)

        elif self.user and self.graph and not self.ai_recommendations:
            seven_petals_company = SevenPetals(company=self.user.company, user=None)

            if members := [usr for usr in self.user.company.members.all() if
                           usr.seven_petals_user.all()]:
                eff = 1 / len(members)
                for user in members:
                    seven_petals_user = user.seven_petals_user.first()
                    seven_petals_company.optimism += (seven_petals_user.optimism * eff)
                    seven_petals_company.stream += (seven_petals_user.stream * eff)
                    seven_petals_company.sense += (seven_petals_user.sense * eff)
                    seven_petals_company.love += (seven_petals_user.love * eff)
                    seven_petals_company.play += (seven_petals_user.play * eff)
                    seven_petals_company.study += (seven_petals_user.study * eff)
                    seven_petals_company.impact += (seven_petals_user.impact * eff)
                    seven_petals_company.general_questions += (
                                seven_petals_user.general_questions * eff)
            seven_petals_company.save()

    def delete(self, *args, **kwargs):
        """Переопределение метода для удаления связанного файла"""
        if self.graph and os.path.isfile(self.graph.path):
            os.remove(self.graph.path)
        super().delete(*args, **kwargs)

    def presentation_data(self, with_clarification: bool = False) -> str:
        """Метод представления данных экземпляра модели в текстовом формате"""
        result = (f"\n<b>Оптимизм</b> - {self.optimism}\n"
                  f"<b>Поток</b> - {self.stream}\n"
                  f"<b>Смысл</b> - {self.sense}\n"
                  f"<b>Любить</b> - {self.love}\n"
                  f"<b>Играть</b> - {self.play}\n"
                  f"<b>Учиться</b> - {self.study}\n"
                  f"<b>Влиять</b> - {self.impact}\n")

        if with_clarification:
            if self.optimism >= 5:
                result += ("\n\n<b>Оптимизм</b> - это личная философия, способ думать, "
                           "особый "
                           "подход к жизненным ситуациям. Это то, насколько вы способны "
                           "видеть ресурсы и возможности, верить в наилучшие перспективы, "
                           "находить творческие решения и позитивные эмоции даже в "
                           "сложных ситуациях")
            if self.impact >= 5.4:
                result += ("\n\n<b>Влиять</b> - значит видеть свою зону влияния и "
                           "фокусировать"
                           " на ней свои мысли и действия. Это про способность быть "
                           "настроенным на победу. Зона влияния есть всегда. Если даже "
                           "в самых сложных ситуациях вы ясно видите, на что вы можете "
                           "влиять, и делаете это, ваша работа будет приносить вам "
                           "удовлетворение")
            if self.play >= 5.5:
                result += ("\n\n<b>Играть</b> - значит относиться к работе, как к игре, "
                           "наполнить ее легкостью и творчеством. Люди, которые умеют "
                           "играть, могут весело и нестандартно решить любую "
                           "сложную задачу")
            if self.sense >= 7.9:
                result += ("\n\n<b>Смысл</b> - это ответ на вопрос «зачем?», ради чего?», "
                           "«во имя чего?» вы делаете то, что вы делаете. Смысл - "
                           "мощнейший источник энергии. Если вы видите в своей работе "
                           "смысл, даже самые неприятные и рутинные дела приносят "
                           "вам радость. Глобальные смыслы в деятельности человека и "
                           "компании дают энергию, фокусируют на главном, помогают "
                           "ставить мотивирующие цели и их достигать")
            if self.play >= 5.5:
                result += ("\n\n<b>Средняя зона:</b>\nЗдесь указано то, что сейчас не "
                           "оказывает большого влияния на ваш уровень счастья на работе. "
                           "Эти области можно развивать\n"
                           "*\tСвобода в планировании рабочего времени\n"
                           "*\tПризнание и благодарность за работу")

            if self.impact >= 5.4:
                result += ("\n\n<b>Зона роста:</b>\nНа эти области стоит обратить внимание"
                           " в первую очередь. Действия в этих направлениях помогут "
                           "быстро увеличить ваш уровень энергии\n"
                           "*\tОптимизм в действии\n"
                           "*\tБаланс жизни и работы")
            if self.ai_recommendations:
                result += f"\n\n<b>Рекомендации от ассистента</b>:\n{self.ai_recommendations}\n"
        return result

    def __repr__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}, "

    def __str__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}"
