import os
import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message

from sqlalchemy.ext.asyncio import AsyncSession

import src.app.keyboard as kb
from src.database.orm_query import orm_get_reminds


router_default_handlers = Router()


@router_default_handlers.message(CommandStart())
async def start(message: Message):
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

# show all reminders as inline buttons
@router_default_handlers.message(Command("menu"))
async def menu(message: Message, session: AsyncSession):
    try:
        reminders = await orm_get_reminds(session)
        if reminders:
            await message.answer("меню", reply_markup=kb.reminders_keyboard(reminders))
        else: await message.answer("нет активных напоминаний")
    except Exception as e:
        await message.answer("Возникла ошибка при выводе напоминаний")
        logging.error(e)
