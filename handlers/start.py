import smtplib
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, ChatTypeFilter
from aiogram.utils.markdown import hlink, hbold

from data.config import ADMINS, WELCOME_TEXT, WELCOME_ASK_IF_TRUE, WELCOME_ASK_PHONE, START_WITHOUT_POST, \
    THANKS_FOR_PHONE, REASK_FOR_PHONE, NO_PHONE_AFTER_2_TIMES, TIME_AFTER_WELCOME_TEXT, TIME_AFTER_POST_ASK, \
    TIME_AFTER_POST_REPLYING, WAIT_FOR_PHONE_2_TIME_IN_SECONDS, WAIT_FOR_PHONE_1_TIME_IN_SECONDS
from keyboards.default.contact_keyboard import contact_keyboard
from loader import dp
from utils.db_api.quick_commands import add_new_user, get_post, update_user_phone, user_mentioned_post, \
    delete_user

import smtplib
from email.mime.text import MIMEText
from environs import Env

from utils.html_email_template import get_html_template

env = Env()
env.read_env()

EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_TO = env.str("EMAIL_TO")
EMAIL_FROM = env.str("EMAIL_FROM")
EMAIL_PASSWORD = env.str("EMAIL_PASSWORD")


def send_email(html_template):
    server = smtplib.SMTP(EMAIL_HOST, 587)
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    msg = MIMEText(html_template, 'html')
    msg['Subject'] = 'Телеграм бот'
    server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
    server.quit()


@dp.message_handler(CommandStart(), ChatTypeFilter(types.ChatType.PRIVATE), state='*')
async def on_start(message: types.Message, state: FSMContext):
    await state.finish()
    deep_link_args = message.get_args()

    if deep_link_args:
        try:
            await add_new_user(
                username=message.from_user.username,
                telegram_id=message.from_user.id,
                phone='',
                posts=[],
                communication=''
            )

            mentioned_post = await get_post(id_=int(deep_link_args))

            await user_mentioned_post(telegram_id=message.from_user.id,
                                      post_id=int(deep_link_args))
            await message.answer(WELCOME_TEXT)
            await asyncio.sleep(TIME_AFTER_WELCOME_TEXT)

            await dp.bot.send_photo(
                chat_id=message.from_user.id,
                photo=mentioned_post.photo_id,
                caption=mentioned_post.text
            )
            await asyncio.sleep(TIME_AFTER_POST_REPLYING)
            await message.answer(WELCOME_ASK_IF_TRUE)
            await asyncio.sleep(TIME_AFTER_POST_ASK)

            await message.answer(WELCOME_ASK_PHONE,
                                 reply_markup=contact_keyboard)
            await state.update_data({'post_id': int(deep_link_args)})
            await state.set_state('wait_for_phone')
        except:
            mentioned_post = await get_post(id_=int(deep_link_args))

            await user_mentioned_post(telegram_id=message.from_user.id,
                                      post_id=int(deep_link_args))
            await message.answer(
                WELCOME_TEXT
            )
            await asyncio.sleep(TIME_AFTER_WELCOME_TEXT)

            await dp.bot.send_photo(
                chat_id=message.from_user.id,
                photo=mentioned_post.photo_id,
                caption=mentioned_post.text
            )
            await asyncio.sleep(TIME_AFTER_POST_REPLYING)
            await message.answer(WELCOME_ASK_IF_TRUE)
            await asyncio.sleep(TIME_AFTER_POST_ASK)

            await message.answer(WELCOME_ASK_PHONE,
                                 reply_markup=contact_keyboard)
            await state.update_data({'post_id': int(deep_link_args)})
            await state.set_state('wait_for_phone')
    else:
        await message.answer(START_WITHOUT_POST)
        await state.set_state('saving_messages')


@dp.message_handler(state='wait_for_phone', content_types=types.ContentType.CONTACT)
@dp.message_handler(state='wait_for_phone', content_types=types.ContentType.ANY)
async def continue_registration(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.CONTACT:
        username = message.from_user.username
        phone = message.contact.phone_number
        await update_user_phone(telegram_id=message.from_user.id, phone=str(phone))
        state_data = await state.get_data()
        post_id = state_data.get('post_id')
        post = await get_post(post_id)
        photo_id = post.photo_id
        post_text = post.text
        post_photo_link = post.photo_link

        html_template = await get_html_template(
            user_phone=phone,
            post_text=post_text,
            photo_link=post_photo_link
        )
        send_email(html_template)
        await dp.bot.send_message(
            chat_id=ADMINS[0],
            text=f'Пользователь {hlink(username, "https://t.me/" + username)} с номером телефона {hbold(phone)} заинтересовался данным постом'
        )

        await dp.bot.send_photo(
            chat_id=ADMINS[0],
            photo=photo_id,
            caption=post_text,
            parse_mode=types.ParseMode.HTML
        )
        await message.answer(THANKS_FOR_PHONE)
        await state.set_state('saving_messages')
    else:
        await asyncio.sleep(WAIT_FOR_PHONE_1_TIME_IN_SECONDS)
        await message.answer(REASK_FOR_PHONE)
        await state.set_state('phone_after_first_remind')


@dp.message_handler(state='phone_after_first_remind', content_types=types.ContentType.ANY)
async def get_phone_again(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.CONTACT:
        username = message.from_user.username
        phone = message.contact.phone_number
        await update_user_phone(telegram_id=message.from_user.id, phone=str(phone))
        state_data = await state.get_data()
        post_id = state_data.get('post_id')
        post = await get_post(post_id)
        photo_id = post.photo_id
        post_text = post.text
        post_photo_link = post.photo_link

        html_template = await get_html_template(
            user_phone=phone,
            post_text=post_text,
            photo_link=post_photo_link
        )
        send_email(html_template)
        await dp.bot.send_message(
            chat_id=ADMINS[0],
            text=f'Пользователь {hlink(username, "https://t.me/" + username)} с номером телефона {hbold(phone)} заинтересовался данным постом'
        )
        await dp.bot.send_photo(
            chat_id=ADMINS[0],
            photo=photo_id,
            caption=post_text,
            parse_mode=types.ParseMode.HTML
        )
        await message.answer(THANKS_FOR_PHONE)
        await state.set_state('saving_messages')
    else:
        await asyncio.sleep(WAIT_FOR_PHONE_2_TIME_IN_SECONDS)
        await message.answer(REASK_FOR_PHONE)
        await state.set_state('get_phone_last_time')


@dp.message_handler(state='get_phone_last_time', content_types=types.ContentType.ANY)
async def get_phone_last_time(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.CONTACT:
        username = message.from_user.username
        phone = message.contact.phone_number
        await update_user_phone(telegram_id=message.from_user.id, phone=str(phone))
        state_data = await state.get_data()
        post_id = state_data.get('post_id')
        post = await get_post(post_id)
        photo_id = post.photo_id
        post_text = post.text
        post_photo_link = post.photo_link

        html_template = await get_html_template(
            user_phone=phone,
            post_text=post_text,
            photo_link=post_photo_link
        )
        send_email(html_template)
        await dp.bot.send_message(
            chat_id=ADMINS[0],
            text=f'Пользователь {hlink(username, "https://t.me/" + username)} с номером телефона {hbold(phone)} заинтересовался данным постом'
        )
        await dp.bot.send_photo(
            chat_id=ADMINS[0],
            photo=photo_id,
            caption=post_text,
            parse_mode=types.ParseMode.HTML
        )
        await message.answer(THANKS_FOR_PHONE)
        await state.set_state('saving_messages')
    else:
        try:
            await delete_user(telegram_id=message.from_user.id)
        except Exception as err:
            print(f'Ошибка при удалении пользователя: {err}')
        await message.answer(NO_PHONE_AFTER_2_TIMES)
        await state.finish()
