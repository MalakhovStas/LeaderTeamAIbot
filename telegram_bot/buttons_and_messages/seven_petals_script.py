"""Модуль формирования сценария опроса 'Семь лепестков'"""
# from importlib import reload
from typing import Optional, List, Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from aiogram.types import InputMediaDocument
from aiogram.types import Message, MediaGroup
# from asgiref.sync import sync_to_async

from config import openai_settings
from core.utils.i18n import I18N
from core.utils.pdf import create_pdf
from psychological_testing.models import SevenPetals
from utils import utils
from .base_classes import BaseButton, BaseMessage
from .openai_menu import QuestionOpenAI
from ..config import SYMS
from ..utils.generate_graph import (
    seven_petals_generate_graph,
    seven_petals_generate_graph_statistics
)
from ..utils.states import FSMSevenPetalsStates


class MessageGetOpenQuestionsIrritation(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:open_questions_irritation'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.end_survey

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        # await sync_to_async(reload)(openai_settings)

        reply_text, next_state = self.reply_text, self.reset_state
        user = update.user
        try:
            await state.update_data({"open_questions_irritation": update.text})
            state_data = await state.get_data()

            seven_petals_user = await SevenPetals.objects.acreate(user=user)

            seven_petals_user.optimism = round(state_data.get("optimism", 0) / 3, 1)
            seven_petals_user.stream = round(state_data.get("stream", 0) / 3, 1)
            seven_petals_user.sense = round(state_data.get("sense", 0) / 3, 1)
            seven_petals_user.love = round(state_data.get("love", 0) / 3, 1)
            seven_petals_user.play = round(state_data.get("play", 0) / 3, 1)
            seven_petals_user.study = round(state_data.get("study", 0) / 3, 1)
            seven_petals_user.impact = round(state_data.get("impact", 0) / 3, 1)
            seven_petals_user.general_questions = state_data.get("general_questions", 0)
            seven_petals_user.open_questions_pleasure = state_data.get("open_questions_pleasure")
            seven_petals_user.open_questions_irritation = state_data.get(
                "open_questions_irritation")

            seven_petals_user.graph = seven_petals_generate_graph(
                seven_petals=seven_petals_user,
                tg_user_id=update.from_user.id
            )

            seven_petals_user.ai_recommendations = await self.ai.some_question(
                prompt=openai_settings.ASSISTANT_RECOMMENDATIONS_PROMPT + seven_petals_user.presentation_data(),
                user_id=update.from_user.id,
            )

            await seven_petals_user.asave()

            seven_petals_generate_graph_statistics(
                all_seven_petals=[
                    test async for test in SevenPetals.objects.filter(user=user).all()
                ],
                tg_user_id=update.from_user.id
            )

            seven_petals_button = SevenPetalsSurveyButton(new=False)
            reply_text, next_state = await seven_petals_button._set_answer_logic(update=update)
            self.children_buttons = seven_petals_button.children_buttons

            # await state.update_data({"open_questions_irritation": update.text})
            # state_data = await state.get_data()
            # user = await (User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).
            #               select_related("seven_petals").afirst())
            # if not user.seven_petals:
            #     user.seven_petals = await SevenPetals.objects.acreate()
            #     await user.asave()
            #
            # user.seven_petals.optimism = round(state_data.get("optimism", 0) / 3, 1)
            # user.seven_petals.stream = round(state_data.get("stream", 0) / 3, 1)
            # user.seven_petals.sense = round(state_data.get("sense", 0) / 3, 1)
            # user.seven_petals.love = round(state_data.get("love", 0) / 3, 1)
            # user.seven_petals.play = round(state_data.get("play", 0) / 3, 1)
            # user.seven_petals.study = round(state_data.get("study", 0) / 3, 1)
            # user.seven_petals.impact = round(state_data.get("impact", 0) / 3, 1)
            # user.seven_petals.general_questions = state_data.get("general_questions", 0)
            # user.seven_petals.open_questions_pleasure = state_data.get("open_questions_pleasure")
            # user.seven_petals.open_questions_irritation = state_data.get(
            #     "open_questions_irritation")
            # await user.seven_petals.asave()
            #
            # graph_path = await seven_petals_generate_graph(tg_user_id=update.from_user.id,
            #                                                seven_petals=user.seven_petals)
            # user.seven_petals.graph = graph_path
            # await user.seven_petals.asave()
            #
            # seven_petals_button = SevenPetalsSurveyButton(new=False)
            # reply_text, next_state = await seven_petals_button._set_answer_logic(update=update)
            # self.children_buttons = seven_petals_button.children_buttons

        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class MessageGetOpenQuestionsPleasure(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:open_questions_pleasure'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.open_questions_irritation

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        try:
            await state.update_data({"open_questions_pleasure": update.text})
            reply_text = I18N(
                ru='Что в вашей текущей работе забирает вашу энергию? В каких ситуациях вы'
                   ' испытываете раздражение, злость, тревогу, страх, напряжение?',
                en='What about your current job is draining your energy? In what situations'
                   ' do you experience irritation, anger, anxiety, fear, tension?',
                style='bold'
            )
            self.children_buttons = []
        except Exception as exc:
            self.log(message=exc, level='error')
        return SYMS.bot_face + reply_text, next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetOpenQuestionsIrritation()]}


class MessageGetGeneralQuestionsHappyInWork(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:general_questions_happy_in_work'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.open_questions_pleasure

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        state_data = await state.get_data()
        try:
            num = int(await utils.data_to_str_digits(update.text) or 0)
            if num < 1 or num > 10:
                reply_text = I18N(
                    ru='Насколько вы в настоящее время счастливы в своей работе?'
                       ' (введите число по шкале от 1 до 10)',
                    en='How happy are you currently in your job?'
                       ' (enter a number on a scale of 1 to 10)',
                    style='bold'
                )
                reply_text += I18N(
                    ru='Оценка должна находится в указанном диапазоне',
                    en='The score must be within the specified range',
                    common_left='\n\n' + SYMS.warning
                )
                self.children_buttons = []
                next_state = FSMSevenPetalsStates.general_questions_happy_in_work
            else:
                await state.update_data(
                    {"general_questions": state_data.get("general_questions") + num})
                reply_text = I18N(
                    ru='Что в вашей текущей работе дает вам энергию, силу,'
                       ' вдохновение, драйв, удовольствие?',
                    en='What about your current job gives you energy, strength,'
                       ' inspiration, drive, pleasure?',
                    style='bold'
                )
                self.children_buttons = []
        except Exception as exc:
            self.log(message=exc, level='error')
        return SYMS.bot_face + reply_text, next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetOpenQuestionsPleasure()]}


class MessageGetGeneralQuestionsHappyMan(BaseMessage):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMSevenPetalsStates:general_questions_happy_man'

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.general_questions_happy_in_work

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        try:
            num = int(await utils.data_to_str_digits(update.text) or 0)
            if num < 1 or num > 10:
                reply_text = I18N(
                    ru='Насколько вы счастливый человек? (введите число по шкале от 1 до 10)',
                    en='How happy are you? (enter a number on a scale of 1 to 10)',
                    style='bold'
                )
                self.children_buttons = []
                next_state = FSMSevenPetalsStates.general_questions_happy_man
            else:
                await state.update_data({"general_questions": num})
                reply_text = I18N(
                    ru='Насколько вы в настоящее время счастливы в своей работе?'
                       ' (введите число по шкале от 1 до 10)',
                    en='How happy are you currently in your job?'
                       ' (enter a number on a scale of 1 to 10)',
                    style='bold'
                )
                self.children_buttons = []

            reply_text += I18N(
                ru='Оценка должна находится в указанном диапазоне',
                en='The score must be within the specified range',
                common_left='\n\n' + SYMS.warning
            )
        except Exception as exc:
            self.log(message=exc, level='error')
        return SYMS.bot_face + reply_text, next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message
                for message in [MessageGetGeneralQuestionsHappyInWork()]}


class SevenPetalsGeneralLogic(BaseButton):
    score = 1_000_000
    score_changeling = -1_000_000

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        current_state = await state.get_state()
        state_data = await state.get_data()

        try:
            if current_state == "FSMSevenPetalsStates:optimism_mobilizing":
                await state.update_data({"optimism": self.score})
                reply_text = I18N(
                    ru='В сложной ситуации я поддерживаю других',
                    en='In difficult situations I support others',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.optimism_support
            elif current_state == "FSMSevenPetalsStates:optimism_support":
                await state.update_data({"optimism": state_data.get("optimism", 0) + self.score})
                reply_text = I18N(
                    ru='Когда что-то идет не так, я чувствую панику, растерянность,'
                       ' хочется все бросить',
                    en='When something goes wrong, I feel panic, confusion,'
                       ' I want to quit everything',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.optimism_changeling
            elif current_state == "FSMSevenPetalsStates:optimism_changeling":
                await state.update_data(
                    {"optimism": state_data.get("optimism", 0) + self.score_changeling})
                reply_text = I18N(
                    ru='Я трачу слишком много времени на скучную и механическую работу',
                    en='I spend too much time on boring and mechanical work',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.stream_changeling

            elif current_state == "FSMSevenPetalsStates:stream_changeling":
                await state.update_data({"stream": self.score_changeling})
                reply_text = I18N(
                    ru='У меня есть возможность заниматься сложными, творческими или'
                       ' стратегическими задачами, требующими концентрации, так,'
                       ' чтобы меня какое-то время никто не отвлекал',
                    en='I have the ability to engage in complex, creative or strategic tasks'
                       ' that require concentration without interruptions for a period of time',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.stream_possibilities

            elif current_state == "FSMSevenPetalsStates:stream_possibilities":
                await state.update_data({"stream": state_data.get("stream", 0) + self.score})
                reply_text = I18N(
                    ru='В деятельности я испытываю ощущение максимальной эффективности'
                       ' - полного погружения в задачу, вдохновения, драйва',
                    en='In my activities, I experience a feeling of maximum efficiency'
                       ' - complete immersion in the task, inspiration, drive',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.stream_efficiency

            elif current_state == "FSMSevenPetalsStates:stream_efficiency":
                await state.update_data({"stream": state_data.get("stream", 0) + self.score})
                reply_text = I18N(
                    ru='Я получаю достойную финансовую отдачу,'
                       ' адекватную моим усилиям и достижениям',
                    en='I receive a decent financial return that is'
                       ' adequate to my efforts and achievements',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.sense_decent_financial_return

            elif current_state == "FSMSevenPetalsStates:sense_decent_financial_return":
                await state.update_data({"sense": self.score})
                reply_text = I18N(
                    ru='Я занимаюсь “своим” делом - тем, что у меня получается лучше всего',
                    en='I do “my” business - what I do best',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.sense_doing_my_own_thing

            elif current_state == "FSMSevenPetalsStates:sense_doing_my_own_thing":
                await state.update_data({"sense": state_data.get("sense", 0) + self.score})
                reply_text = I18N(
                    ru='Я сомневаюсь, что делаю что-то стоящее, что-то, что улучшает жизнь людей',
                    en="I doubt I'm doing anything worthwhile,"
                       " anything that improves people's lives",
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.sense_changeling

            elif current_state == "FSMSevenPetalsStates:sense_changeling":
                await state.update_data(
                    {"sense": state_data.get("sense", 0) + self.score_changeling})
                reply_text = I18N(
                    ru='На работе я не могу быть самим собой,'
                       ' я скорее играю какую-то не свойственную мне роль',
                    en='At work I can’t be myself, I rather play some role'
                       ' that is not typical for me',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.love_changeling

            elif current_state == "FSMSevenPetalsStates:love_changeling":
                await state.update_data({"love": self.score_changeling})
                reply_text = I18N(
                    ru='У меня хорошие, неконфликтные отношения с моим деловым окружением'
                       ' (руководство, коллеги, партнеры, клиенты)',
                    en='I have good, non-conflict relationships with my business environment'
                       ' (management, colleagues, partners, clients)',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.love_good_relation

            elif current_state == "FSMSevenPetalsStates:love_good_relation":
                await state.update_data({"love": state_data.get("love", 0) + self.score})
                reply_text = I18N(
                    ru='Я получаю признание и благодарность за свою работу от моего делового'
                       ' окружения (руководителя, коллег, партнеров, клиентов)',
                    en='I receive recognition and gratitude for my work from my business'
                       ' environment (manager, colleagues, partners, clients)',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.love_confession

            elif current_state == "FSMSevenPetalsStates:love_confession":
                await state.update_data({"love": state_data.get("love", 0) + self.score})
                reply_text = I18N(
                    ru='Для меня деятельность - это игра. Я не воспринимаю слишком серьезно'
                       ' свои неудачи или успехи, с юмором отношусь к себе,'
                       ' создаю вокруг обстановку легкости и позитива',
                    en='For me, activity is a game. I don’t take my failures or successes too'
                       ' seriously, I treat myself with humor, and I create an atmosphere'
                       ' of lightness and positivity around me.',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.play_activity_is_game

            elif current_state == "FSMSevenPetalsStates:play_activity_is_game":
                await state.update_data({"play": self.score})
                reply_text = I18N(
                    ru='У меня получается творчески, нестандартно решать'
                       ' даже скучные или очень сложные задачи',
                    en='I am able to creatively and unconventionally solve'
                       ' even boring or very complex problems.',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.play_creative

            elif current_state == "FSMSevenPetalsStates:play_creative":
                await state.update_data({"play": state_data.get("play", 0) + self.score})
                reply_text = I18N(
                    ru='Я стремлюсь все сделать идеально,'
                       ' из-за чего испытываю стресс и напряжение',
                    en='I strive to do everything perfectly, which causes me stress and tension.',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.play_changeling

            elif current_state == "FSMSevenPetalsStates:play_changeling":
                await state.update_data(
                    {"play": state_data.get("play", 0) + self.score_changeling})
                reply_text = I18N(
                    ru='Мне интересно, потому что в работе постоянно возникают новые задачи,'
                       ' и я получаю новый опыт',
                    en='I’m interested because new tasks constantly arise in my work,'
                       ' and I gain new experience',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.study_new_experience

            elif current_state == "FSMSevenPetalsStates:study_new_experience":
                await state.update_data({"study": self.score})
                reply_text = I18N(
                    ru='Я чувствую, что перестал(а) развиваться, мне не хватает возможностей'
                       ' для карьерного, профессионального роста',
                    en='I feel that I have stopped developing, I lack opportunities for'
                       ' career and professional growth',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.study_changeling

            elif current_state == "FSMSevenPetalsStates:study_changeling":
                await state.update_data(
                    {"study": state_data.get("study", 0) + self.score_changeling})
                reply_text = I18N(
                    ru='В своей деятельности я могу делать то, что мне действительно нравится',
                    en='In my activity I can do what I really like',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.study_do_what_i_like

            elif current_state == "FSMSevenPetalsStates:study_do_what_i_like":
                await state.update_data({"study": state_data.get("study", 0) + self.score})
                reply_text = I18N(
                    ru='Я могу самостоятельно планировать свою работу - влиять на '
                       'постановку задачи, сроки и способы ее выполнения',
                    en='I can independently plan my work - influence the setting of the task,'
                       ' the timing and methods of its implementation',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.impact_to_plan

            elif current_state == "FSMSevenPetalsStates:impact_to_plan":
                await state.update_data({"impact": self.score})
                reply_text = I18N(
                    ru='Я слишком много работаю и не успеваю уделять внимание себе,'
                       ' своей семье и своим интересам',
                    en="I work too much and don't have time to pay attention to myself,"
                       " my family and my interests",
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.impact_changeling

            elif current_state == "FSMSevenPetalsStates:impact_changeling":
                await state.update_data(
                    {"impact": state_data.get("impact", 0) + self.score_changeling})
                reply_text = I18N(
                    ru='Я достигаю поставленных целей и вижу реальные результаты своей работы',
                    en='I achieve my goals and see real results from my work',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.impact_achieve_my_goals

            elif current_state == "FSMSevenPetalsStates:impact_achieve_my_goals":
                await state.update_data({"impact": state_data.get("impact", 0) + self.score})
                reply_text = I18N(
                    ru='Оцените, пожалуйста, насколько вы счастливый человек? '
                       '(введите число по шкале от 1 до 10)',
                    en='Please rate how happy you are? (enter a number on a scale of 1 to 10)',
                    style='bold'
                )
                next_state = FSMSevenPetalsStates.general_questions_happy_man
                self.children_buttons = []
                self.children_messages = {message.state_or_key: message
                                          for message in [MessageGetGeneralQuestionsHappyMan()]}
        except Exception as exc:
            self.log(message=exc, level='error')
        return SYMS.bot_face + reply_text, next_state

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

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Практически никогда',
            en='Almost never',
        )


class VeryRarelyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Очень редко'"""
    score = 1.667
    score_changeling = -8.335

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Очень редко',
            en='Very rarely',
        )


class RarelyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Редко'"""
    score = 3.334
    score_changeling = -6.668

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Редко',
            en='Rarely',
        )


class SometimesFiftyFiftyButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Иногда 50/50'"""
    score = 5
    score_changeling = -5

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Иногда 50/50',
            en='Sometimes 50/50',
        )


class OftenButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Часто'"""
    score = 6.668
    score_changeling = -3.334

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Часто',
            en='Often',
        )


class VeryOftenButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Очень часто'"""
    score = 8.335
    score_changeling = -1.667

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Очень часто',
            en='Very often',
        )


class AlmostAlwaysButton(SevenPetalsGeneralLogic, BaseButton):
    """Класс описывающий кнопку - 'Практически всегда'"""
    score = 10
    score_changeling = 0

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Практически всегда',
            en='Almost always',
        )


class SevenPetalsNewSurveyButton(BaseButton):
    """Класс описывающий кнопку - 'Пройти опрос заново'"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Пройти опрос',
            en='Take the survey',
            common_left=SYMS.ball_asterisk,
        )

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.optimism_mobilizing

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='В сложной ситуации я мобилизуюсь, ищу решение, '
               'пробую разные способы достижения цели',
            en='In a difficult situation, I mobilize, look for a solution, '
               'try different ways to achieve the goal',
            style='bold',
            common_left=SYMS.bot_face
        )

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


class DownloadPDF(BaseButton):
    """Класс описывающий кнопку - 'Выгрузить результаты тестирования'"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Выгрузить результаты тестирования PDF',
            en='Download test results PDF',
            common_left=SYMS.download,
        )

    def _set_next_state(self) -> str:
        # return FSMSevenPetalsStates.start_survey
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text, next_state = self.reply_text, self.next_state
        user = update.user
        try:
            path = create_pdf(
                test=await user.seven_petals_user.afirst(),
                tg_user_id=update.from_user.id
            )

            media = MediaGroup()
            media.attach(InputMediaDocument(open(path, 'rb')))
            await self.bot.send_media_group(chat_id=update.from_user.id, media=media)

            reply_text = I18N(
                ru='Ваши результаты тестирования',
                en='Your test results',
                style='bold'
            )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class SevenPetalsSurveyButton(BaseButton):
    """Класс описывающий кнопку - 'Опрос Семь лепестков'"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Опрос - Семь лепестков',
            en='Survey - Seven Petals',
            common_left=SYMS.ball_asterisk,
        )

    def _set_next_state(self) -> str:
        return FSMSevenPetalsStates.start_survey

    def _set_reply_text(self) -> Union[str, I18N]:
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
        user = update.user
        try:
            last_testing_seven_petals_user = await user.seven_petals_user.afirst()

            if not last_testing_seven_petals_user:
                reply_text = I18N(
                    ru='Чтобы получить результаты необходимо пройти опрос',
                    en='To get results you must complete the survey',
                    style='bold'
                )
            else:
                await self.delete_prev_message_and_send_graph(
                    tg_user_id=update.from_user.id,
                    graph_filename=last_testing_seven_petals_user.graph.path
                )
                reply_text = I18N(
                    ru='Результат опроса',
                    en='Survey result',
                    style='bold',
                    common_left=SYMS.bot_face,
                    common_right=':\n' + last_testing_seven_petals_user.presentation_data(
                        with_clarification=True
                    )
                )
                # if last_testing_seven_petals_user.optimism >= 5:
                #     reply_text += ("\n\n<b>Оптимизм</b> - это личная философия, способ думать, "
                #                    "особый "
                #                    "подход к жизненным ситуациям. Это то, насколько вы способны "
                #                    "видеть ресурсы и возможности, верить в наилучшие перспективы, "
                #                    "находить творческие решения и позитивные эмоции даже в "
                #                    "сложных ситуациях")

                # if last_testing_seven_petals_user.impact >= 5.4:
                #     reply_text += ("\n\n<b>Влиять</b> - значит видеть свою зону влияния и "
                #                    "фокусировать"
                #                    " на ней свои мысли и действия. Это про способность быть "
                #                    "настроенным на победу. Зона влияния есть всегда. Если даже "
                #                    "в самых сложных ситуациях вы ясно видите, на что вы можете "
                #                    "влиять, и делаете это, ваша работа будет приносить вам "
                #                    "удовлетворение")

                # if last_testing_seven_petals_user.play >= 5.5:
                #     reply_text += ("\n\n<b>Играть</b> - значит относиться к работе, как к игре, "
                #                    "наполнить ее легкостью и творчеством. Люди, которые умеют "
                #                    "играть, могут весело и нестандартно решить любую "
                #                    "сложную задачу")

                # if last_testing_seven_petals_user.sense >= 7.9:
                #     reply_text += ("\n\n<b>Смысл</b> - это ответ на вопрос «зачем?», ради чего?», "
                #                    "«во имя чего?» вы делаете то, что вы делаете. Смысл - "
                #                    "мощнейший источник энергии. Если вы видите в своей работе "
                #                    "смысл, даже самые неприятные и рутинные дела приносят "
                #                    "вам радость. Глобальные смыслы в деятельности человека и "
                #                    "компании дают энергию, фокусируют на главном, помогают "
                #                    "ставить мотивирующие цели и их достигать")
                # if last_testing_seven_petals_user.play >= 5.5:
                #     reply_text += ("\n\n<b>Средняя зона:</b>\nЗдесь указано то, что сейчас не "
                #                    "оказывает большого влияния на ваш уровень счастья на работе. "
                #                    "Эти области можно развивать\n"
                #                    "*\tСвобода в планировании рабочего времени\n"
                #                    "*\tПризнание и благодарность за работу")
                #
                # if last_testing_seven_petals_user.impact >= 5.4:
                #     reply_text += ("\n\n<b>Зона роста:</b>\nНа эти области стоит обратить внимание"
                #                    " в первую очередь. Действия в этих направлениях помогут "
                #                    "быстро увеличить ваш уровень энергии\n"
                #                    "*\tОптимизм в действии\n"
                #                    "*\tБаланс жизни и работы")

                # reply_text += f"\n\n Рекомендации от ассистента:\n тут "
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state

    def _set_children(self) -> List:

        return [
            SevenPetalsNewSurveyButton(parent_name=self.class_name),
            QuestionOpenAI(new=False),
            DownloadPDF(),
        ]
