from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from fastapi.params import Body
from random import randrange

app = FastAPI()


#  NOW lets do pydantic validation for body
class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # default is true
    rating: Optional[int] = None  # options field and default is none


my_posts = [
    {"title": "Title of post 1", "content": "Content of post 1", "id": 1},
    {"title": "Title of post 2", "content": "Content of post 2", "id": 2},
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


@app.post("/createposts")
# extract all data from req body, type cast to dict and store in payload
async def create_post(payload: dict = Body()):
    return {
        "message": f"You did {payload['type']} from {payload['account']} account on {payload['date']} amount of {payload['amount']}"
    }


# pydantic automatically gets data for us
@app.post("/pydantic/create_post")
# post here is stored as pydantic model
async def pydantic_create_post(post: Post):
    print(post)
    # convert pydantic model to dictionary
    print(post.model_dump())

    # for crud
    post_dict = post.model_dump()
    # add id field with random number of converted dict from pydantic model
    post_dict["id"] = randrange(1, 1000000)
    # add or append new data to our database ie. our array for now
    my_posts.append(post_dict)

    return {"message": "Successfully created"}


# CRUD
@app.get("/posts")
def get_posts():
    # Fast api automatically searialize the array to json
    return {"data": my_posts}


@app.get("/posts/latest")
def get_latest_post():
    latest = my_posts[len(my_posts) - 1]
    return {"latest_post": latest}


# id is path parameter
@app.get("/posts/{id}")
# we dont need to create response here if we throw HTTPException
def get_post(id: int, response: Response):
    post = find_post(id)

    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"Error": f"post with id {id} was not found!"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            # here name of message must be detail
            detail=f"post with id {id} was not found!",
        )

    return {"data": post}
