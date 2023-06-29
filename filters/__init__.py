from aiogram import Dispatcher

from .channel_filter import IsChannel
from .admin_filter import IsAdmin


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsChannel)
