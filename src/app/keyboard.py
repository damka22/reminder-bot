from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


add_agree = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить', callback_data="Agree"),
     InlineKeyboardButton(text='❌ Отменить', callback_data="Disagree")]
])

choose_lang = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]],
    resize_keyboard=True,
)


def reminders_keyboard(reminders):
    keyboard = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=remind.text[:30], callback_data=f"remind_{remind.id}")
        for remind in reminders
    ]
    keyboard.add(*buttons)
    return keyboard.adjust(2).as_markup()


def edit_remind_keyboard(remind):
    remind_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔁 Изменить', callback_data=f"change_{remind.id}"),
         InlineKeyboardButton(text='❌ Удалить', callback_data=f"delete_{remind.id}")],
        [InlineKeyboardButton(text='◀️ Назад', callback_data="back_to_menu")],
    ])
    return remind_keyboard