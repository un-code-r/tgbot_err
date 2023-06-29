from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from integrations.telegraph import TelegraphService
from utils.db_api.postgresql import db
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
file_uploader = TelegraphService()

__all__ = ["bot", "storage", "dp", "db"]
