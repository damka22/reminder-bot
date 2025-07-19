from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config.config import TIMEZONE
from common.constants import months

def set_time(data: dict) -> dict:
    wait_time: int = int(data['time'])
    end_time: datetime = datetime.now(tz=ZoneInfo(TIMEZONE)) + timedelta(minutes=float(wait_time))
    data['end_time']: str = f"{end_time.day} {months[end_time.month]} {end_time.strftime('%H:%M')}" # по красоте str
    data['remind_at']: datetime = end_time # формат datetime
    return data