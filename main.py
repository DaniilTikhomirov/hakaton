from typing import Annotated, List

from fastapi.params import Body, Depends
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from database.models import Base, User, Queue
from database.database import engine
from database.schemas import User as dbUser, QueueCreate, Queue as dbQueue
from service import (get_db, add_to_queue, del_from_queue, get_queue_users_amount_by_title)
from service import (get_queue_user_from_title, notification)
from bot import bot, dp


app = FastAPI()

Base.metadata.create_all(bind=engine)
user_name = "dania43"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users/", response_model=List[dbUser])
async def get_users(db: Session = Depends(get_db)) -> List[User] | List:
    db_users = db.query(User).all()
    return db_users

@app.post("/registration")
async def get_registration(username: str):
    global user_name
    user_name = username
    return {"name": user_name}

@app.get("/queue", response_model=List[dbQueue])
async def get_queue(db: Session = Depends(get_db)) -> List[dbQueue] | List:
    db_queue = db.query(Queue).all()
    return db_queue


@app.post("/queue/add")
async def update_queue(queue: Annotated[QueueCreate, Body(..., exempl={
    "title": "test1"
})], db: Session = Depends(get_db)) -> dbQueue:
    db_queue = await add_to_queue(queue, db, user_name=user_name)
    await notification(db=db, bot=bot, dp=dp)
    return db_queue

@app.delete("/queue/del")
async def quit_queue(db: Session = Depends(get_db)):
    await notification(db=db, bot=bot, dp=dp)
    await del_from_queue(db, user_name=user_name)

@app.post("/queue/users/count")
async def get_amount_people(title: str, db: Session = Depends(get_db)) -> int:
    return await get_queue_users_amount_by_title(db, title)

@app.post("/queue/users/time")
async def get_time_queue(title: str, db: Session = Depends(get_db)) -> int:
    return await get_queue_users_amount_by_title(db, title) * 10

@app.post("/queue/users", response_model=List[dbQueue])
async def get_user_from_title(title: str, db: Session = Depends(get_db)) -> List:
    return await get_queue_user_from_title(db, title)



