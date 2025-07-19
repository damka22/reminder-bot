from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter

from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboard import edit_remind_keyboard, reminders_keyboard
from database.orm_query import orm_add_remind, orm_delete_remind, orm_get_remind, orm_get_reminds
from common.time_helper import set_time
from app.remind_handlers import Remind

router_callbacks = Router()

@router_callbacks.callback_query(F.data == "Agree")
async def agree_add(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        data = await state.get_data()
        data = set_time(data)
        await state.clear()

        # record to database
        await orm_add_remind(session, data, callback.from_user.id)
        await callback.message.edit_text(f"Ок! Напомню через {data['time']} минут.", reply_markup=None)
        await callback.answer("Подтверждено")
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text("Возникла ошибка при добавлении напоминания", reply_markup=None)
        print(f"!!!There was an error adding the reminder: {e} !!!")

@router_callbacks.callback_query(F.data == "Disagree")
async def disagree_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Отмена")
    await callback.message.edit_text("Отменено", reply_markup=None)

@router_callbacks.callback_query(F.data.startswith("remind_"))
async def open_remind(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    try:
        ID_remind = int(callback.data.split("_")[-1])
        obj = await orm_get_remind(session, ID_remind, callback.from_user.id)
        remind_kb = edit_remind_keyboard(obj)
        await callback.message.edit_text(f"{obj.text} — {obj.remind_at_str}", reply_markup=remind_kb)
    except Exception as e:
        await callback.message.answer("Возникла ошибка при выводе напоминания")

@router_callbacks.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_remind(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    ID_remind = int(callback.data.split("_")[-1])

    remind_for_change = await orm_get_remind(session, ID_remind, callback.from_user.id)
    Remind.remind_for_change = remind_for_change

    await callback.answer()
    await callback.message.answer("Введите текст напоминания", reply_markup=None)
    await state.set_state(Remind.text)

@router_callbacks.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, session: AsyncSession):
    await callback.answer("меню")
    reminders = await orm_get_reminds(session)
    if reminders:
        await callback.message.edit_text("меню", reply_markup=reminders_keyboard(reminders))
    else: await callback.message.edit_text("нет активных напоминаний")

@router_callbacks.callback_query(F.data.startswith("delete_"))
async def delete_remind(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    ID_remind = int(callback.data.split("_")[-1])

    await orm_delete_remind(session, ID_remind, callback.from_user.id)
    
    reminders = await orm_get_reminds(session)
    if reminders:
        await callback.message.edit_text("меню", reply_markup=reminders_keyboard(reminders))
    else:
        await callback.message.edit_text("нет активных напоминаний")