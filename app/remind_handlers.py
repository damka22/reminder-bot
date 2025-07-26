import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import dateparser

from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboard as kb
from database.orm_query import orm_update_remind
from common.time_helper import set_beutfiul_time
from config.config import TIMEZONE
from common.preprocess_time import preprocess_time_input

router_remind_handlers = Router()

class Remind(StatesGroup):
    text: str = State()
    time: str = State()
    wait_agree_or_disagree: None = State()

    remind_for_change = None

@router_remind_handlers.message(Command("add"))
async def add_remind(message: Message, state: FSMContext):
    await state.set_state(Remind.text)
    await message.answer("<i>Что мне напомнить?</i>", parse_mode="html")

# when entering reminder text/time you can cancel everything and not save the reminder
@router_remind_handlers.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    if current_state is None:
        return
    if Remind.remind_for_change:
        Remind.remind_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=None)

@router_remind_handlers.message(Remind.text)
async def first_process_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Отправьте текстовое напоминание")
        return
    if Remind.remind_for_change and message.text == '.':
        await state.update_data(text=Remind.remind_for_change.text)
    else:
        await state.update_data(text=message.text)
    await state.set_state(Remind.time)
    await message.answer("<i>Через сколько минут напомнить?</i>\n\n"
                         "Примеры формата времени:\n\n"
                         "• через 15 минут\n"
                         "• сегодня в 18:30\n"
                         "• 21 июля в 14:00", parse_mode='HTML')

@router_remind_handlers.message(Remind.time)
async def second_process_time(message: Message, state: FSMContext, session: AsyncSession):
    if Remind.remind_for_change and message.text == '.':
        await state.update_data(time=Remind.remind_for_change.time)
    else:
        try:
            processed_text = preprocess_time_input(message.text) # чтобы работало с утром/вечером и тд
            date_parsed = dateparser.parse(
                processed_text,
                languages=["ru"],
                settings={"TIMEZONE": TIMEZONE,
                          "RETURN_AS_TIMEZONE_AWARE": True,
                          }
            )
            now = datetime.now(tz=ZoneInfo(TIMEZONE))
            if date_parsed is None:
                await message.reply("Введите правильный формат времени.")
                return
            elif date_parsed < now:
                await message.reply("Нельзя установить напоминание в прошлом.")
                return
            elif date_parsed - now > timedelta(days=31):
                await message.reply("Слишком далёкая дата. Максимум — 1 месяц вперёд.")
                return
            await state.update_data(time=date_parsed)
        except ValueError:
            await message.reply("Введите правильный формат времени.")
            return
        except Exception as e:
            await message.answer("Произошла ошибка, напоминание не записано.")
            logging.error(f"Ошибка записи напоминания {e}")
            await state.clear()
            return
    data = await state.get_data()
    data = set_beutfiul_time(data) # делаем красоту в remind_at_str
    try:
        if Remind.remind_for_change:
            # если изменяем, то без agree/disagree, вручную дописываем данные в data
            if data['time'] == Remind.remind_for_change.time:
                # если время не менялось
                data['end_time'] = Remind.remind_for_change.remind_at_str
                data['remind_at'] = Remind.remind_for_change.remind_at
                remind_id = Remind.remind_for_change.id
                await orm_update_remind(session, remind_id, message.from_user.id, data)
                await state.clear()
                await message.answer("Напоминание изменено")
            else:
                # время поменялось и надо по новой делать время(в функции)
                remind_id = Remind.remind_for_change.id
                await orm_update_remind(session, remind_id, message.from_user.id, data)
                await state.clear()
                await message.answer(f"Напоминание изменено\n<{data['text']}> {data['remind_at_str']}")
        else:
            # процесс создания нового, идем дальше в callbacks -> agree/disagree
            await message.answer(f"Создать напоминание <{data['text']}> {data['remind_at_str']}?",
                                 reply_markup=kb.add_agree)
            await state.set_state(Remind.wait_agree_or_disagree)
    except Exception as e:
        await message.answer(
            f"Возникла ошибка\nОбратись к программисту",
            reply_markup=None,
        )
        await state.clear()
        logging.error(f"Ошибка с записью в бд: {e}")
    Remind.remind_for_change = None

@router_remind_handlers.message(Remind.wait_agree_or_disagree)
async def wait_end_of_process(message: Message, state: FSMContext):
    # при создании нового напоминания тут ждем пока нажмет на agree/disagree или напишет "отмена" и
    # напоминание отменится
    await message.answer("Выберите действие с новым напоминанием"
                         "\n\nили напишите <b>'отмена'</b> для отмены напоминания", parse_mode="HTML")


