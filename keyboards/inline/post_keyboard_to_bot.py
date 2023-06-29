from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import BOT_USERNAME


async def generate_post_keyboard(post_id: str):
    new_post_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕', url=f'https://t.me/{BOT_USERNAME}?start={post_id}'
                )
            ]
        ]
    )
    return new_post_keyboard
