from aiogram.dispatcher.filters.state import StatesGroup, State


class PostPublicationState(StatesGroup):
    post_text = State()
    post_image = State()
    post_confirmation = State()


class PostPublicationOnTimeState(StatesGroup):
    post_text = State()
    post_image = State()
    post_time = State()
    post_confirmation = State()
