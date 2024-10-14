from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    number = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    telegram_id = Column(Integer, index=True)


class Queue(Base):
    __tablename__ = 'queue'

    title = Column(String, unique=False)
    userId = Column(Integer, ForeignKey('users.telegram_id'), index=True,
                    primary_key=True, unique=True)
    ticket = Column(Integer, index=True)
