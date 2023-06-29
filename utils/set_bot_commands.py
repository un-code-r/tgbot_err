from aiogram import types
from aiogram.types import BotCommandScopeAllChatAdministrators


async def set_user_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Начать работу"),
        ]
    )

