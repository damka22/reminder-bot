from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboard as kb
from database.orm_query import orm_update_remind
from common.time_helper import set_time


router_remind_handlers = Router()

class Remind(StatesGroup):
    text: str = State()
    time: str = State()
    wait_agree_or_disagree: None = State()

    remind_for_change = None

@router_remind_handlers.message(Command("add"))
async def add_remind(message: Message, state: FSMContext):
    await state.set_state(Remind.text)
    await message.answer("Что мне напомнить?")

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
    await message.answer("Через сколько минут напомнить?")

@router_remind_handlers.message(Remind.time)
async def second_process_time(message: Message, state: FSMContext, session: AsyncSession):
    if Remind.remind_for_change and message.text == '.':
        await state.update_data(time=Remind.remind_for_change.time)
    else:
        try:
            delta_minutes = int(message.text)
            if delta_minutes < 1 or delta_minutes > 1440:
                await message.reply("Время должно быть не меньше 1 и не больше 1440 минут.")
                return
            await state.update_data(time=message.text)
        except ValueError:
            await message.reply("Введите целое число минут.")
            return
        except Exception as e:
            await message.answer("Произошла ошибка, напоминание не записано.")
            await state.clear()
            return

    data = await state.get_data()

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
                data = set_time(data)

                remind_id = Remind.remind_for_change.id
                await orm_update_remind(session, remind_id, message.from_user.id, data)
                await state.clear()
                await message.answer(f"Напоминание изменено\n<{data['text']}> через {data['time']} минут")

        else:
            # создаем новое, идем дальше в callbacks -> agree/disagree
            wait_time = int(data['time'])
            text = data['text']
            await message.answer(f"Создать напоминание <{text}> через {wait_time} минут?",
                                 reply_markup=kb.add_agree)
            await state.set_state(Remind.wait_agree_or_disagree)

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру",
            reply_markup=None,
        )
        await state.clear()

    Remind.remind_for_change = None

@router_remind_handlers.message(Remind.wait_agree_or_disagree)
async def wait_end_of_process(message: Message, state: FSMContext):
    # при создании нового напоминания тут ждем пока нажмет на agree/disagree или напишет "отмена" и
    # напоминание отменится
    await message.answer("Выберите действие с новым напоминанием"
                         "\n\nили напишите <b>'отмена'</b> для отмены напоминания", parse_mode="HTML")


