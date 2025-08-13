from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    ...


class Remind(Base):
    __tablename__ = "remind"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id в бд
    tg_id: Mapped[int] # tg id
    text: Mapped[str] # текст напоминания
    time: Mapped[datetime] # формат datetime когда будет напоминание (было тупо минуты)
    remind_at_str: Mapped[str] # по красоте типо так <19 Июля 17:59>
    status: Mapped[str] = mapped_column(String, default="active") # ну статус (active или done)