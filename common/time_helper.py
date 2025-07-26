from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config.config import TIMEZONE
from common.constants import months

def set_beutfiul_time(data: dict) -> dict:
    data['remind_at_str']: str = f"{data['time'].day} {months[data['time'].month]} {data['time'].strftime('%H:%M')}"
    return data
