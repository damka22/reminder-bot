import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from database.engine import session_maker
from database.models import Remind
from database.orm_query import orm_delete_remind
from config.config import TIMEZONE

# каждые 5 секунд проверяет бд
# напоминания у которых статус active и их время(time) меньше текущего - пишет пользователю
async def reminder_scheduler(bot):
    while True:
        async with session_maker() as session:
            now = datetime.now(tz=ZoneInfo(TIMEZONE))

            result = await session.execute(
                select(Remind).where(Remind.time <= now,
                                     Remind.status == "active")
            )
            reminders = result.scalars().all()

            to_delete = await session.execute(
                select(Remind).where(Remind.time <= now - timedelta(days=1),
                                     Remind.status != "active")
            )
            to_delete = to_delete.scalars().all()

            for remind in reminders:
                try:
                    await bot.send_message(chat_id=remind.tg_id, text=f"⏰ Напоминание: {remind.text}")
                    remind.status = "done"
                except Exception as e:
                    print(f"Ошибка при отправке напоминания: {e}")

            for remind in to_delete:
                try:
                    await orm_delete_remind(session, remind.id, remind.tg_id)
                except Exception as e:
                    print(f"Ошибка при удалении напоминания: {e}")

            await session.commit()

        await asyncio.sleep(5)
