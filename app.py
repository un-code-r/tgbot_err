from aiogram import executor, Dispatcher
import filters
from integrations.telegraph import FileUploader
from middlewares.integration import IntegrationMiddleware
from utils.db_api import postgresql
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_user_commands
from loader import db, file_uploader


async def on_startup(dp: Dispatcher):
    print('Установка соединения с БД...')
    await postgresql.on_startup(dp)
    print('Успешно!')

    print("Создаем таблицы")
    await db.gino.create_all()
    print("Готово")

    filters.setup(dp)
    dp.middleware.setup(IntegrationMiddleware(file_uploader))
    await set_user_commands(dp)
    await on_startup_notify(dp)


async def on_shutdown(dp: Dispatcher):
    fileUploader: FileUploader = file_uploader
    await fileUploader.close()


if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
