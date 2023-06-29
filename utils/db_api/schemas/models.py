from sqlalchemy.orm import relationship

from utils.db_api.postgresql import TimedBaseModel, BaseModel
from sqlalchemy import Column, BigInteger, String, sql, Text, ARRAY, Integer


class User(TimedBaseModel):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    phone = Column(Text, unique=True, nullable=True)
    posts = Column(ARRAY(item_type=Integer, as_tuple=True))
    communication = Column(Text)

    query: sql.Select


class Post(BaseModel):
    __tablename__ = 'posts'

    id = Column(BigInteger, primary_key=True)
    text = Column(Text, nullable=False)
    photo_id = Column(Text, nullable=False)
    photo_link = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=False)

    query: sql.Select
