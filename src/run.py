import asyncio
import logging

from src.config.config import TOKEN, ADMIN_ID

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from src.app.callbacks import router_callbacks
from src.app.default_handlers import router_default_handlers
from src.app.remind_handlers import router_remind_handlers
from src.common.bot_cmd_list import private_chat
from src.common.scheduler import reminder_scheduler
from src.database.engine import create_db, drop_db, session_maker
from src.middlewares.db import DataBaseSession

dp = Dispatcher()

# clear all records from db, can only admin
@dp.message(Command("clear"), F.from_user.id==ADMIN_ID)
async def clear_bd(message: types.Message):
    await drop_db()
    await message.answer('—————\nall db clear\n—————')

async def main():
    logging.basicConfig(level=logging.WARNING)
    # logging errors sqlalchemy
    error_logger = logging.getLogger("sqlalchemy")
    error_logger.setLevel(logging.WARNING)

    bot = Bot(token=TOKEN)
    dp.include_router(router_remind_handlers)  # FSM router handlers
    dp.include_router(router_default_handlers)  # other router handlers
    dp.include_router(router_callbacks)  # router callback

    await create_db()
    asyncio.create_task(reminder_scheduler(bot))

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private_chat, scope=types.BotCommandScopeAllPrivateChats())
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Bot start polling...")
    logging.getLogger().setLevel(logging.WARNING)
    await dp.start_polling(bot)