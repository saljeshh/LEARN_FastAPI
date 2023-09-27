from pydantic import BaseModel
from datetime import datetime


# pydantic validation


# usin inheritance
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    # pass measns same as post base
    pass


# for response .. if user send id and pass . we dont wanna send back them password
# for this purpose we have datavalidatrion to send back as well
class Post(PostBase):
    # baki field haru mathi postBase bata inherit vayeraxa
    # bhakar send gareko ho vanera bhakar ko time pathako yo .. not from database
    created_at: datetime

    # see in docs sql wala ma
    # convert sql alchemy model to pydantic model or dict
    class Config:
        orm_mode = True
