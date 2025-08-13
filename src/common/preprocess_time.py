import re

def preprocess_time_input(text: str) -> str:
    """Предобработка времени для dateparser"""
    processed = text.strip()

    # Заменяем пробелы в времени на двоеточия
    processed = re.sub(r'\b(\d{1,2})\s+(\d{2})\b', r'\1:\2', processed)

    # Заменяем неточные времена на конкретные
    time_mappings = {
        'утром': 'в 9:00',
        'днем': 'в 14:00',
        'вечером': 'в 19:00',
        'ночью': 'в 23:00'
    }

    for vague, specific in time_mappings.items():
        processed = processed.replace(vague, specific)

    return processed