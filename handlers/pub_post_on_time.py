import pytz
import datetime

import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from data.config import CHANNEL_ID
from filters import IsAdmin
from keyboards.inline.post_keyboard_to_bot import generate_post_keyboard
from keyboards.inline.post_keybooards import confirm_post_keyboard_on_time
from loader import dp, file_uploader
from states.post_publication import PostPublicationOnTimeState
from utils.db_api.quick_commands import add_new_post, get_post_id
from utils.upload_photo import photo_upload


@dp.message_handler(Command('publicate_post_on_time'), IsAdmin(), state='*')
async def start_publicating_post(message: types.Message):
    await message.answer('Введите текст публикации: ')
    await PostPublicationOnTimeState.post_text.set()


@dp.message_handler(state=PostPublicationOnTimeState.post_text)
async def get_image(message: types.Message, state: FSMContext):
    post_text = message.text
    await state.update_data(post_text=post_text)

    await message.answer('Прикрепите изображение для публикации')

    await PostPublicationOnTimeState.post_image.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=PostPublicationOnTimeState.post_image)
async def get_post_image(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    photo_link = await photo_upload(message, file_uploader)

    await state.update_data(photo_link=photo_link)
    await state.update_data(post_photo=photo_id)
    await message.answer('Укажите дату и время публикации поста в формате ГГГГ/ММ/ДД ЧЧ:ММ (время МСК)')
    await PostPublicationOnTimeState.post_time.set()


@dp.message_handler(regexp='[0-9]{1,4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}',
                    content_types=types.ContentType.TEXT, state=PostPublicationOnTimeState.post_time)
async def get_post_time(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    photo_id = state_data.get('post_photo')
    post_text = state_data.get('post_text')
    post_time = message.text
    await state.update_data(post_time=post_time)
    await message.answer('Вот так будет опубликован Ваш пост в назначенное время')
    await message.answer_photo(photo=photo_id,
                               caption=post_text,
                               parse_mode=types.ParseMode.HTML)
    await message.answer('Вы действительно хотите опубликовать данный пост?', reply_markup=confirm_post_keyboard_on_time)
    await PostPublicationOnTimeState.post_confirmation.set()


@dp.callback_query_handler(state=PostPublicationOnTimeState.post_confirmation, text='yes_pub_post_on_time')
async def publicate_post(call: CallbackQuery, state: FSMContext):
    try:
        post_data = await state.get_data()
        post_text = post_data.get('post_text')
        post_photo = post_data.get('post_photo')
        post_time = post_data.get('post_time')
        photo_link = post_data.get('photo_link')

        # 2023/06/23 17:30

        pt = post_time.split(' ')
        post_date = pt[0]
        post_clock = pt[1]
        year = post_date.split('/')[0]
        month = post_date.split('/')[1]
        day = post_date.split('/')[2]

        hours = post_clock.split(':')[0]
        minutes = post_clock.split(':')[1]

        offset = datetime.timedelta(hours=3)
        tz_moscow = datetime.timezone(offset, name='МСК')

        now_date = datetime.datetime.now(tz=tz_moscow)
        future_date = datetime.datetime(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hours),
            minute=int(minutes),
            tzinfo=tz_moscow
        )

        time_diff = future_date - now_date
        sleep_seconds = time_diff.seconds

        print(sleep_seconds)

        await state.finish()
        await call.message.edit_text(text='Пост будет опубликован к указанному времени')

        await asyncio.sleep(sleep_seconds)

        await add_new_post(
            text=post_text, photo_id=post_photo, photo_link=photo_link, telegram_id=call.message.message_id
        )
        post_id = await get_post_id(post_text)

        post_markup = await generate_post_keyboard(post_id=post_id)
        await dp.bot.send_photo(
            chat_id=CHANNEL_ID,
            caption=post_text,
            photo=post_photo,
            reply_markup=post_markup,
            parse_mode=types.ParseMode.HTML
        )
    except Exception as err:
        print(f'Ошибка при отправке поста -> {err}')
        await call.message.edit_text(text='Ошибка при отправке поста...')
        await state.finish()


@dp.callback_query_handler(state=PostPublicationOnTimeState.post_confirmation, text='no_pub_post_on_time')
async def dont_publicate_post(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.answer('Вы отменили публикацию поста!')
    await state.finish()
