import asyncio
import logging

from config.config import TOKEN, ADMIN_ID

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from app.callbacks import router_callbacks
from app.default_handlers import router_default_handlers
from app.remind_handlers import router_remind_handlers
from common.bot_cmd_list import private_chat
from common.scheduler import reminder_scheduler
from database.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router_remind_handlers) # FSM router handlers
dp.include_router(router_default_handlers) # other router handlers
dp.include_router(router_callbacks) # router callback

# clear all records from db, can only admin
@dp.message(Command("clear"), F.from_user.id==ADMIN_ID)
async def clear_bd(message: types.Message):
    await drop_db()
    await message.answer('—————\nall db clear\n—————')

async def main():
    await create_db()
    asyncio.create_task(reminder_scheduler(bot))

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private_chat, scope=types.BotCommandScopeAllPrivateChats())

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    # logging errors sqlalchemy
    error_logger = logging.getLogger("sqlalchemy")
    error_logger.setLevel(logging.WARNING)

    print('Start')
    try: asyncio.run(main())
    except KeyboardInterrupt: print('Exit')