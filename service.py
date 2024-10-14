from mailbox import Message
from typing import Annotated, List

from fastapi import Body, Depends
from sqlalchemy.orm import Session

from aiogram import Bot, Dispatcher, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from asyncio import sleep

from database.database import session_local
from database.schemas import QueueCreate, Queue as dbQueue
from database.models import Queue, User
from fastapi import HTTPException


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def find_id_by_name(db: Session, user_name: str):
    user_id = db.query(User).filter(User.name == user_name).first()
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id.telegram_id


async def add_to_queue(queue: Annotated[QueueCreate, Body(..., exempl={
    "title": "test1"
})], db: Session, user_name: str) -> dbQueue:
    user_id = find_id_by_name(db, user_name)
    ticket = db.query(Queue).filter_by(title=queue.title).all()
    max_ticket = max([t.ticket for t in ticket] + [0]) + 1
    existing_entry = db.query(Queue).filter_by(userId=user_id).first()
    if existing_entry is None:
        db_queue = Queue(userId=user_id, title=queue.title, ticket=max_ticket)
        db.add(db_queue)
        db.commit()
        db.refresh(db_queue)
        return db_queue
    print("bad user")
    if existing_entry.title != queue.title:
        existing_entry.ticket = max_ticket
    existing_entry.title = queue.title
    db.commit()
    db.refresh(existing_entry)
    return existing_entry


async def find_position(db: Session, user_name: str) -> int:
    user_id = find_id_by_name(db, user_name)
    user_position = db.query(Queue).filter_by(userId=user_id).first().ticket
    return user_position

async def position_drop(db: Session, user_position: int):
    drop = db.query(Queue).filter(Queue.ticket > user_position).all()
    for user in drop:
        user.ticket -= 1
    db.commit()


async def del_from_queue(db: Session, user_name: str):
    user_id = find_id_by_name(db, user_name)
    queue_delete = db.query(Queue).filter_by(userId=user_id).first()
    if queue_delete:
        user_position = await find_position(db, user_name)
        db.delete(queue_delete)
        db.commit()
        await position_drop(db, user_position)
    else:
        raise HTTPException(status_code=404, detail="Queue not found")

async def get_amount_users_of_queue(db: Session):
    return db.query(Queue).count()

async def get_queue_users_amount_by_title(db: Session, queue_name: str) -> int:
    users = db.query(Queue).filter_by(title=queue_name).count()
    return users - 1 if users > 0 else users



async def get_queue_user_from_title(db: Session, queue_name: str) -> List:
    return db.query(Queue).filter_by(title=queue_name).all()


async def notification(db: Session, bot: Bot, dp: Dispatcher):
    buttons = [[KeyboardButton(text='Я забрал заказ')]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=buttons)
    db_lst = db.query(Queue).all()
    for queue in db_lst:
        if queue.ticket == 1:
            await bot.send_message(chat_id=str(queue.userId), text=f'Ваш заказ готов', reply_markup=keyboard)
            await sleep(3)
        elif queue.ticket == 2:
            await bot.send_message(chat_id=str(queue.userId), text=f'Будьте внимательны, перед вами остался один человек')
        elif queue.ticket == 3:
            await bot.send_message(chat_id=str(queue.userId), text=f'Будьте внимательны, перед вами осталось два человека')

