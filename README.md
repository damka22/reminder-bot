# reminder-bot

Простой Telegram-бот на Python, который помогает ставить напоминания и не забывать важные дела.

## Что это за проект

`reminder-bot` — это небольшой учебно-практический проект.  
Идея простая: пользователь пишет боту, что и когда напомнить, а бот в нужное время отправляет сообщение.

## Как это работает (простыми словами)

1. Вы отправляете боту команду/сообщение с текстом напоминания и временем.
2. Бот сохраняет это напоминание.
3. Фоновая логика (планировщик) проверяет, не пора ли что-то отправить.
4. Когда время наступает — бот присылает вам сообщение в Telegram.

## Основные возможности

- добавление напоминаний;
- хранение напоминаний до нужного времени;
- отправка уведомлений в нужный момент;
- запуск локально и через Docker.

## Стек

- **Python** (основной код бота)
- **Docker** (для удобного запуска в контейнере)

## Что нужно перед запуском

1. Установленный **Python 3.10+**.
2. Токен Telegram-бота.
3. Установленный Docker, если хотите запускать в контейнере.

## Настройка окружения

Пример:

```env
TOKEN=123:ABC# TOKEN your bot in BOTfather
DB_LITE=sqlite+aiosqlite:///reminder_bot/data/my_base.db# name of you db
TIMEZONE=Asia/Yekaterinburg# your timezone
```



## Запуск локально (без Docker)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/damka22/reminder-bot.git
   cd reminder-bot
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv .venv
   ```

   Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```

   Windows (PowerShell):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте `.env` и добавьте токен бота.

5. Запустите бота:
   ```bash
   python run.py
   ```


## Запуск через Docker

### Вариант 1: Docker

1. Соберите образ:
   ```bash
   docker build -t reminder-bot .
   ```

2. Запустите контейнер:
   ```bash
   docker run --env-file .env --name reminder-bot --rm reminder-bot
   ```

### Вариант 2: Docker Compose

```bash
docker compose up --build
```

## Пример использования

После запуска:
1. Откройте вашего бота в Telegram.
2. Нажмите `/start`.
3. Отправьте напоминание в формате, который поддерживает бот.
4. Дождитесь сообщения в указанное время.
