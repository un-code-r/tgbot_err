from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.db_api.quick_commands import update_user_communication


@dp.message_handler(state='saving_messages', content_types=types.ContentType.TEXT)
async def save_all_messages(message: types.Message, state: FSMContext):
    await update_user_communication(telegram_id=message.from_user.id,
                                    new_communication=message.text)
