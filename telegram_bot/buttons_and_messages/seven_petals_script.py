"""Модуль формирования сценаярия ороса 'Семь лепестков'"""
from typing import Optional, List, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from aiogram.types import Message

from psychological_testing.models import SevenPetals
from users.models import User
from .base_classes import BaseButton, BaseMessage
from .openai_menu import QuestionOpenAI
from ..config import FACE_BOT
from ..utils.generate_graph import seven_petals_generate_graph
# from ..utils.misc_utils import check_data
from ..utils.states import FSMSevenPetalsStates
from utils import utils


class MessageGetOpenQuestionsIrritation(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:open_questions_irritation'

    def _set_next_state(self) -> str:
        # return self.reset_state
        return FSMSevenPetalsStates.end_survey

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.reset_state
        try:
            await state.update_data({"open_questions_irritation": update.text})
            state_data = await state.get_data()
            user = await (User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).
                          select_related("seven_petals").afirst())
            if not user.seven_petals:
                user.seven_petals = await SevenPetals.objects.acreate()
                await user.asave()

            user.seven_petals.optimism = round(state_data.get("optimism", 0) / 3, 1)
            user.seven_petals.stream = round(state_data.get("stream", 0) / 3, 1)
            user.seven_petals.sense = round(state_data.get("sense", 0) / 3, 1)
            user.seven_petals.love = round(state_data.get("love", 0) / 3, 1)
            user.seven_petals.play = round(state_data.get("play", 0) / 3, 1)
            user.seven_petals.study = round(state_data.get("study", 0) / 3, 1)
            user.seven_petals.impact = round(state_data.get("impact", 0) / 3, 1)
            user.seven_petals.general_questions = state_data.get("general_questions", 0)
            user.seven_petals.open_questions_pleasure = state_data.get("open_questions_pleasure")
            user.seven_petals.open_questions_irritation = state_data.get(
                "open_questions_irritation")
            await user.seven_petals.asave()

            graph_path = await seven_petals_generate_graph(tg_user_id=update.from_user.id,
                                                           seven_petals=user.seven_petals)
            user.seven_petals.graph = graph_path
            await user.seven_petals.asave()

            seven_petals_button = SevenPetalsSurveyButton(new=False)
            reply_text, next_state = await seven_petals_button._set_answer_logic(update=update)
            self.children_buttons = seven_petals_button.children_buttons

        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state


class MessageGetOpenQuestionsPleasure(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:open_questions_pleasure'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.open_questions_irritation

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        try:
            await state.update_data({"open_questions_pleasure": update.text})
            reply_text = ("<b>Что в вашей текущей работе забирает вашу энергию? "
                          "В каких ситуациях вы испытываете раздражение, злость, "
                          "тревогу, страх, напряжение?</b>")
            self.children_buttons = []
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{reply_text}', next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetOpenQuestionsIrritation()]}


class MessageGetGeneralQuestionsHappyInWork(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:general_questions_happy_in_work'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.open_questions_pleasure

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        state_data = await state.get_data()
        try:
            num = int(await utils.data_to_str_digits(update.text) or 0)
            if num < 1 or num > 10:
                reply_text = ("⚠ Оценка должна находится в указанном диапазоне\n\n"
                              "<b>Насколько вы в настоящее время счастливы в своей работе? "
                              "(введите число по шкале от 1 до 10)</b>")
                self.children_buttons = []
                next_state = FSMSevenPetalsStates.general_questions_happy_in_work
            else:
                await state.update_data(
                    {"general_questions": state_data.get("general_questions") + num})
                reply_text = ("<b>Что в вашей текущей работе дает вам энергию, "
                              "силу, вдохновение, драйв, удовольствие?</b>")
                self.children_buttons = []
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{reply_text}', next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetOpenQuestionsPleasure()]}


class MessageGetGeneralQuestionsHappyMan(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:general_questions_happy_man'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.general_questions_happy_in_work

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        try:
            num = int(await utils.data_to_str_digits(update.text) or 0)
            if num < 1 or num > 10:
                reply_text = ("⚠ Оценка должна находится в указанном диапазоне\n\n"
                              "<b>Насколько вы счастливый человек? "
                              "(введите число по шкале от 1 до 10)</b>")
                self.children_buttons = []
                next_state = FSMSevenPetalsStates.general_questions_happy_man
            else:
                await state.update_data({"general_questions": num})
                reply_text = ("<b>Насколько вы в настоящее время счастливы в своей работе? "
                              "(введите число по шкале от 1 до 10)</b>")
                self.children_buttons = []
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{reply_text}', next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message
                for message in [MessageGetGeneralQuestionsHappyInWork()]}


class SevenPetalsGeneralLogic(BaseButton):
    score = 1_000_000
    score_changeling = -1_000_000

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        current_state = await state.get_state()
        state_data = await state.get_data()
        try:
            if current_state == "FSMSevenPetalsStates:optimism_mobilizing":
                await state.update_data({"optimism": self.score})
                reply_text = "<b>В сложной ситуации я поддерживаю других</b>"
                next_state = FSMSevenPetalsStates.optimism_support
            elif current_state == "FSMSevenPetalsStates:optimism_support":
                await state.update_data({"optimism": state_data.get("optimism", 0) + self.score})
                reply_text = ("<b>Когда что-то идет не так, я чувствую панику, "
                              "растерянность, хочется все бросить</b>")
                next_state = FSMSevenPetalsStates.optimism_changeling
            elif current_state == "FSMSevenPetalsStates:optimism_changeling":
                await state.update_data(
                    {"optimism": state_data.get("optimism", 0) + self.score_changeling})
                reply_text = ("<b>Я трачу слишком много времени на "
                              "скучную и механическую работу</b>")
                next_state = FSMSevenPetalsStates.stream_changeling

            elif current_state == "FSMSevenPetalsStates:stream_changeling":
                await state.update_data({"stream": self.score_changeling})
                reply_text = ("<b>У меня есть возможность заниматься сложными, творческими или "
                              "стратегическими задачами, требующими концентрации, "
                              "так, чтобы меня какое-то время никто не отвлекал</b>")
                next_state = FSMSevenPetalsStates.stream_possibilities

            elif current_state == "FSMSevenPetalsStates:stream_possibilities":
                await state.update_data({"stream": state_data.get("stream", 0) + self.score})
                reply_text = ("<b>В деятельности я испытываю ощущение максимальной эффективности"
                              " - полного погружения в задачу, вдохновения, драйва</b>")
                next_state = FSMSevenPetalsStates.stream_efficiency

            elif current_state == "FSMSevenPetalsStates:stream_efficiency":
                await state.update_data({"stream": state_data.get("stream", 0) + self.score})
                reply_text = ("<b>Я получаю достойную финансовую отдачу, "
                              "адекватную моим усилиям и достижениям</b>")
                next_state = FSMSevenPetalsStates.sense_decent_financial_return

            elif current_state == "FSMSevenPetalsStates:sense_decent_financial_return":
                await state.update_data({"sense": self.score})
                reply_text = ("<b>Я занимаюсь “своим” делом - тем, "
                              "что у меня получается лучше всего</b>")
                next_state = FSMSevenPetalsStates.sense_doing_my_own_thing

            elif current_state == "FSMSevenPetalsStates:sense_doing_my_own_thing":
                await state.update_data({"sense": state_data.get("sense", 0) + self.score})
                reply_text = ("<b>Я сомневаюсь, что делаю что-то стоящее, "
                              "что-то, что улучшает жизнь людей</b>")
                next_state = FSMSevenPetalsStates.sense_changeling

            elif current_state == "FSMSevenPetalsStates:sense_changeling":
                await state.update_data(
                    {"sense": state_data.get("sense", 0) + self.score_changeling})
                reply_text = ("<b>На работе я не могу быть самим собой, "
                              "я скорее играю какую-то не свойственную мне роль</b>")
                next_state = FSMSevenPetalsStates.love_changeling

            elif current_state == "FSMSevenPetalsStates:love_changeling":
                await state.update_data({"love": self.score_changeling})
                reply_text = ("<b>У меня хорошие, неконфликтные отношения с моим "
                              "деловым окружением (руководство, коллеги, партнеры, клиенты)</b>")
                next_state = FSMSevenPetalsStates.love_good_relation

            elif current_state == "FSMSevenPetalsStates:love_good_relation":
                await state.update_data({"love": state_data.get("love", 0) + self.score})
                reply_text = ("<b>Я получаю признание и благодарность за свою работу от моего "
                              "делового окружения (руководителя, коллег, партнеров, клиентов)</b>")
                next_state = FSMSevenPetalsStates.love_confession

            elif current_state == "FSMSevenPetalsStates:love_confession":
                await state.update_data({"love": state_data.get("love", 0) + self.score})
                reply_text = ("<b>Для меня деятельность - это игра. Я не воспринимаю слишком "
                              "серьезно свои неудачи или успехи, с юмором отношусь к себе, "
                              "создаю вокруг обстановку легкости и позитива</b>")
                next_state = FSMSevenPetalsStates.play_activity_is_game

            elif current_state == "FSMSevenPetalsStates:play_activity_is_game":
                await state.update_data({"play": self.score})
                reply_text = ("<b>У меня получается творчески, нестандартно решать "
                              "даже скучные или очень сложные задачи</b>")
                next_state = FSMSevenPetalsStates.play_creative

            elif current_state == "FSMSevenPetalsStates:play_creative":
                await state.update_data({"play": state_data.get("play", 0) + self.score})
                reply_text = ("<b>Я стремлюсь все сделать идеально, "
                              "из-за чего испытываю стресс и напряжение</b>")
                next_state = FSMSevenPetalsStates.play_changeling

            elif current_state == "FSMSevenPetalsStates:play_changeling":
                await state.update_data(
                    {"play": state_data.get("play", 0) + self.score_changeling})
                reply_text = ("<b>Мне интересно, потому что в работе постоянно "
                              "возникают новые задачи, и я получаю новый опыт</b>")
                next_state = FSMSevenPetalsStates.study_new_experience

            elif current_state == "FSMSevenPetalsStates:study_new_experience":
                await state.update_data({"study": self.score})
                reply_text = ("<b>Я чувствую, что перестал(а) развиваться, мне не хватает "
                              "возможностей для карьерного, профессионального роста</b>")
                next_state = FSMSevenPetalsStates.study_changeling

            elif current_state == "FSMSevenPetalsStates:study_changeling":
                await state.update_data(
                    {"study": state_data.get("study", 0) + self.score_changeling})
                reply_text = ("<b>В своей деятельности я могу делать то, "
                              "что мне действительно нравится</b>")
                next_state = FSMSevenPetalsStates.study_do_what_i_like

            elif current_state == "FSMSevenPetalsStates:study_do_what_i_like":
                await state.update_data({"study": state_data.get("study", 0) + self.score})
                reply_text = ("<b>Я могу самостоятельно планировать свою работу - влиять на "
                              "постановку задачи, сроки и способы ее выполнения</b>")
                next_state = FSMSevenPetalsStates.impact_to_plan

            elif current_state == "FSMSevenPetalsStates:impact_to_plan":
                await state.update_data({"impact": self.score})
                reply_text = ("<b>Я слишком много работаю и не успеваю уделять внимание себе, "
                              "своей семье и своим интересам</b>")
                next_state = FSMSevenPetalsStates.impact_changeling

            elif current_state == "FSMSevenPetalsStates:impact_changeling":
                await state.update_data(
                    {"impact": state_data.get("impact", 0) + self.score_changeling})
                reply_text = ("<b>Я достигаю поставленных целей и вижу "
                              "реальные результаты своей работы</b>")
                next_state = FSMSevenPetalsStates.impact_achieve_my_goals

            elif current_state == "FSMSevenPetalsStates:impact_achieve_my_goals":
                await state.update_data({"impact": state_data.get("impact", 0) + self.score})
                reply_text = ("<b>Оцените, пожалуйста, насколько вы "
                              "счастливый человек? (введите число по шкале от 1 до 10)</b>")
                next_state = FSMSevenPetalsStates.general_questions_happy_man
                self.children_buttons = []
                self.children_messages = {message.state_or_key: message
                                          for message in [MessageGetGeneralQuestionsHappyMan()]}
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{reply_text}', next_state

    def _set_children(self) -> List:

        return [
            PracticallyNeverButton(new=False),
            VeryRarelyButton(new=False),
            RarelyButton(new=False),
            SometimesFiftyFiftyButton(new=False),
            OftenButton(new=False),
            VeryOftenButton(new=False),
            AlmostAlwaysButton(new=False),
        ]


class PracticallyNeverButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Практически никогда'"""

    score = 0
    score_changeling = -10

    def _set_name(self) -> str:
        return 'Практически никогда'


class VeryRarelyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Очень редко'"""
    score = 1.667
    score_changeling = -8.335

    def _set_name(self) -> str:
        return 'Очень редко'


class RarelyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Редко'"""
    score = 3.334
    score_changeling = -6.668

    def _set_name(self) -> str:
        return 'Редко'


class SometimesFiftyFiftyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Иногда 50/50'"""
    score = 5
    score_changeling = -5

    def _set_name(self) -> str:
        return 'Иногда 50/50'


class OftenButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Часто'"""
    score = 6.668
    score_changeling = -3.334

    def _set_name(self) -> str:
        return 'Часто'


class VeryOftenButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Очень часто'"""
    score = 8.335
    score_changeling = -1.667

    def _set_name(self) -> str:
        return 'Очень часто'


class AlmostAlwaysButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Практически всегда'"""
    score = 10
    score_changeling = 0

    def _set_name(self) -> str:
        return 'Практически всегда'


class SevenPetalsNewSurveyButton(BaseButton):
    """Класс описывающий кнопку - 'Пройти опрос заново'"""

    def _set_name(self) -> str:
        return 'Пройти опрос'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.optimism_mobilizing

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + ('<b>В сложной ситуации я мобилизуюсь, ищу решение, '
                           'пробую разные способы достижения цели</b>')

    def _set_children(self) -> List:
        return [
            PracticallyNeverButton(parent_name=self.class_name),
            VeryRarelyButton(parent_name=self.class_name),
            RarelyButton(parent_name=self.class_name),
            SometimesFiftyFiftyButton(parent_name=self.class_name),
            OftenButton(parent_name=self.class_name),
            VeryOftenButton(parent_name=self.class_name),
            AlmostAlwaysButton(parent_name=self.class_name),
        ]


class SevenPetalsSurveyButton(BaseButton):
    """Класс описывающий кнопку - 'Опрос Семь лепестков'"""

    def _set_name(self) -> str:
        return '❉ \t Опрос - Семь лепестков'

    def _set_next_state(self) -> str:
        # return self.reset_state
        return FSMSevenPetalsStates.start_survey

    def _set_reply_text(self) -> Optional[str]:
        return self.default_error

    async def delete_prev_message_and_send_graph(
            self, tg_user_id: int, graph_filename: str) -> None:
        """Удаляет последнее сообщение от бота пользователю и отправляет ему график"""
        from telegram_bot.handlers.handlers import delete_message

        if last_message_id := await self.button_search_and_action_any_collections(
                user_id=tg_user_id, action='get',
                button_name='last_handler_sent_message_id', updates_data=True):
            await delete_message(chat_id=tg_user_id, message_id=last_message_id)

        await self.bot.send_photo(chat_id=tg_user_id, photo=InputFile(graph_filename))

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        try:
            user = await (User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).
                          select_related("seven_petals").afirst())
            if not user.seven_petals:
                reply_text = "<b>Чтобы получить результаты необходимо пройти опрос</b>"
            else:
                await self.delete_prev_message_and_send_graph(
                    tg_user_id=update.from_user.id, graph_filename=user.seven_petals.graph.path)

                reply_text = (f"{FACE_BOT}<b>Результат опроса:</b>\n\n"
                              f"<b>Оптимизм</b> - {user.seven_petals.optimism}\n"
                              f"<b>Поток</b> - {user.seven_petals.stream}\n"
                              f"<b>Смысл</b> - {user.seven_petals.sense}\n"
                              f"<b>Любить</b> - {user.seven_petals.love}\n"
                              f"<b>Играть</b> - {user.seven_petals.play}\n"
                              f"<b>Влиять</b> - {user.seven_petals.impact}\n")
                if user.seven_petals.optimism >= 5:
                    reply_text += ("\n\n<b>Оптимизм</b> - это личная философия, способ думать, "
                                   "особый "
                                   "подход к жизненным ситуациям. Это то, насколько вы способны "
                                   "видеть ресурсы и возможности, верить в наилучшие перспективы, "
                                   "находить творческие решения и позитивные эмоции даже в "
                                   "сложных ситуациях")
                if user.seven_petals.impact >= 5.4:
                    reply_text += ("\n\n<b>Влиять</b> - значит видеть свою зону влияния и "
                                   "фокусировать"
                                   " на ней свои мысли и действия. Это про способность быть "
                                   "настроенным на победу. Зона влияния есть всегда. Если даже "
                                   "в самых сложных ситуациях вы ясно видите, на что вы можете "
                                   "влиять, и делаете это, ваша работа будет приносить вам "
                                   "удовлетворение")
                if user.seven_petals.play >= 5.5:
                    reply_text += ("\n\n<b>Играть</b> - значит относиться к работе, как к игре, "
                                   "наполнить ее легкостью и творчеством. Люди, которые умеют "
                                   "играть, могут весело и нестандартно решить любую "
                                   "сложную задачу")
                if user.seven_petals.sense >= 7.9:
                    reply_text += ("\n\n<b>Смысл</b> - это ответ на вопрос «зачем?», ради чего?», "
                                   "«во имя чего?» вы делаете то, что вы делаете. Смысл - "
                                   "мощнейший источник энергии. Если вы видите в своей работе "
                                   "смысл, даже самые неприятные и рутинные дела приносят "
                                   "вам радость. Глобальные смыслы в деятельности человека и "
                                   "компании дают энергию, фокусируют на главном, помогают "
                                   "ставить мотивирующие цели и их достигать")

                if user.seven_petals.play >= 5.5:
                    reply_text += ("\n\n<b>Средняя зона:</b>\nЗдесь указано то, что сейчас не "
                                   "оказывает большого влияния на ваш уровень счастья на работе. "
                                   "Эти области можно развивать\n"
                                   "*\tСвобода в планировании рабочего времени\n"
                                   "*\tПризнание и благодарность за работу")

                if user.seven_petals.impact >= 5.4:
                    reply_text += ("\n\n<b>Зона роста:</b>\nНа эти области стоит обратить внимание"
                                   " в первую очередь. Действия в этих направлениях помогут "
                                   "быстро увеличить ваш уровень энергии\n"
                                   "*\tОптимизм в действии\n"
                                   "*\tБаланс жизни и работы")
        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state

    def _set_children(self) -> List:

        return [
            SevenPetalsNewSurveyButton(parent_name=self.class_name),
            QuestionOpenAI(new=False)
        ]
