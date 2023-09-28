from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# pydantic validation


# --   Schema for User
class UserCreate(BaseModel):
    email: EmailStr  # checks its valid email or not
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        # convert sql alchemy model to pydantic model or dict orm mode paila
        from_attribute = True


# usin inheritance
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    # pass measns same as post base
    owner_id: int
    pass


# for response .. if user send id and pass . we dont wanna send back them password
# for this purpose we have datavalidatrion to send back as well
class Post(PostBase):
    id: int
    # baki field haru mathi postBase bata inherit vayeraxa
    # bhakar send gareko ho vanera bhakar ko time pathako yo .. not from database
    created_at: datetime
    owner_id: int
    # to get user
    owner: UserOut

    # see in docs sql wala ma
    # convert sql alchemy model to pydantic model or dict
    class Config:
        from_attribute = True


# for auth
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# for user bata aune token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
