import os

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from sqlalchemy.ext.asyncio import AsyncSession

import app.keyboard as kb
from database.orm_query import orm_get_reminds


router_default_handlers = Router()

class ChangeLang(StatesGroup):
    lang: str = State()


@router_default_handlers.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    # if user not in db, create it

    await message.reply("Hola!")

# по приколу пока что фотка
@router_default_handlers.message(Command("help"))
async def help_msg(message: Message):
    try:
        photo_path = "pictures/help_tyan.jpg"
        if not os.path.exists(photo_path):
            raise FileNotFoundError
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption="ステップ左、ステップ右-2ステップ")
    except Exception:
        await message.answer("ステップ左、ステップ右-2ステップ")

# show all reminders as inline button
@router_default_handlers.message(Command("menu"))
async def menu(message: Message, session: AsyncSession):
    reminders = await orm_get_reminds(session)
    if reminders:
        await message.answer("меню", reply_markup=kb.reminders_keyboard(reminders))
    else: await message.answer("нет активных напоминаний")
