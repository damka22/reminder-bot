import sys

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.models import Base, Remind
from src.config.config import DB_LITE


try:
    engine = create_async_engine(DB_LITE)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
except Exception as e:
    print(f"Error with creating database: {e}")
    # if error with db -> stop all bot
    sys.exit(1)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# clear all records from db, can only admin
async def drop_db():
    async with session_maker() as session:
        await session.execute(delete(Remind))
        await session.commit()