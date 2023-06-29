from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.config import PHONE_KEYBOARD_TEXT

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=PHONE_KEYBOARD_TEXT, request_contact=True)
        ]
    ],
    resize_keyboard=True
)