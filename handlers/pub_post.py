from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from data.config import CHANNEL_ID
from filters import IsAdmin
from keyboards.inline.post_keyboard_to_bot import generate_post_keyboard
from keyboards.inline.post_keybooards import confirm_post_keyboard
from loader import dp, file_uploader
from states.post_publication import PostPublicationState
from utils.db_api.quick_commands import add_new_post, get_post_id
from utils.upload_photo import photo_upload


@dp.message_handler(Command('publicate_post'), IsAdmin(), state='*')
async def start_publicating_post(message: types.Message):
    await message.answer('Введите текст публикации: ')
    await PostPublicationState.post_text.set()


@dp.message_handler(state=PostPublicationState.post_text)
async def get_image(message: types.Message, state: FSMContext):
    post_text = message.text
    await state.update_data(post_text=post_text)

    await message.answer('Прикрепите изображение для публикации')

    await PostPublicationState.post_image.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=PostPublicationState.post_image)
async def collecting_all_post_data(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    photo_id = message.photo[-1].file_id
    post_text = state_data.get('post_text')
    photo_link = await photo_upload(message, file_uploader)

    await state.update_data(post_photo=photo_id)
    await state.update_data(photo_link=photo_link)
    await message.answer('Вот так будет опубликован Ваш пост')
    await message.answer_photo(photo=photo_id,
                               caption=post_text,
                               parse_mode=types.ParseMode.HTML)
    await message.answer('Вы действительно хотите опубликовать данный пост?', reply_markup=confirm_post_keyboard)
    await PostPublicationState.post_confirmation.set()


@dp.callback_query_handler(state=PostPublicationState.post_confirmation, text='yes_pub_post')
async def publicate_post(call: CallbackQuery, state: FSMContext):
    try:
        post_data = await state.get_data()
        post_text = post_data.get('post_text')
        post_photo = post_data.get('post_photo')
        photo_link = post_data.get('photo_link')

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

        await state.finish()
        await call.message.edit_text(text='Вы успешно опубликовали пост!')
    except Exception as err:
        print(f'Ошибка при отправке поста -> {err}')
        await call.message.edit_text(text='Ошибка при отправке поста...')
        await state.finish()


@dp.callback_query_handler(state=PostPublicationState.post_confirmation, text='no_pub_post')
async def dont_publicate_post(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.answer('Вы отменили публикацию поста!')
    await state.finish()
