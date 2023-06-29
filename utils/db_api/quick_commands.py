from utils.db_api.schemas.models import User, Post


async def add_new_user(username: str,
                       telegram_id: int,
                       phone: str,
                       posts: list,
                       communication: str):
    try:
        user = User(username=username,
                    telegram_id=telegram_id,
                    phone=phone,
                    posts=posts,
                    communication=communication)
        await user.create()
    except:
        print('Ошибка при создании пользователя!')


async def get_user(telegram_id: int):
    user = await User.query.where(User.telegram_id == telegram_id).gino.first()
    return user


async def delete_user(telegram_id: int):
    return await User.delete.where(User.telegram_id == telegram_id).gino.status()


async def update_user_phone(telegram_id: int, phone: str):
    user = await User.query.where(User.telegram_id == telegram_id).gino.first()
    await user.update(phone=phone).apply()


async def update_user_communication(telegram_id: int, new_communication: str):
    user = await User.query.where(User.telegram_id == telegram_id).gino.first()
    communication = user.communication
    communication += f' | {new_communication} |'
    await user.update(communication=communication).apply()


async def user_mentioned_post(telegram_id: int, post_id: int):
    user = await User.query.where(User.telegram_id == telegram_id).gino.first()
    posts = user.posts
    posts += (post_id,)
    await user.update(posts=posts).apply()
    # user = await get_user(telegram_id=telegram_id)
    # list(user.posts).append(post_id)


async def add_new_post(text: str, photo_id: str, photo_link: str, telegram_id: int):
    try:
        post = Post(text=text, photo_id=photo_id, photo_link=photo_link, telegram_id=telegram_id)
        await post.create()
    except:
        print('Ошибка при создании поста!')


async def get_post(id_: int):
    post = await Post.query.where(Post.id == id_).gino.first()
    return post


async def get_post_id(text: str):
    post = await Post.query.where(Post.text == text).gino.first()
    return post.id
