from typing import Annotated, Optional, List

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: Annotated[
        str, Field(..., title="имя пользовотеля", min_length=2, max_length=50)
    ]

    telegram_id: Annotated[
        int, Field(..., title="id пользователя", ge=0)
    ]


class User(UserBase):
    number: Annotated[
        int, Field(..., title="талон номера очереди", ge=1)
    ]

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class QueueBase(BaseModel):
    title: Annotated[str, Field(..., title="название очереди")]


class Queue(QueueBase):
    userId: Annotated[int, Field(..., title="участник очереди")]
    ticket: Annotated[int, Field(..., title="номер в очереди", ge=1)]




    class Config:
        orm_mode = True


class QueueCreate(QueueBase):
    pass


class UserName(BaseModel):
    name: str