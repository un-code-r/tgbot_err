from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_post_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Да', callback_data='yes_pub_post'),
            InlineKeyboardButton('Нет (сбросить)', callback_data='no_pub_post')
        ]
    ]
)

confirm_post_keyboard_on_time = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Да', callback_data='yes_pub_post_on_time'),
            InlineKeyboardButton('Нет (сбросить)', callback_data='no_pub_post_on_time')
        ]
    ]
)
