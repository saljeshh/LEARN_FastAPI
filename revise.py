from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()


# pydantic validation
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


# Fake database
my_posts = [
    {"id": 1, "title": "Title of Post 1", "content": "content of Post 1"},
    {"id": 2, "title": "Title of Post 2", "content": "content of Post 2"},
    {"id": 3, "title": "Title of Post 3", "content": "content of Post 3"},
]


# Functino to find data from the database
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


# rest api -----------------


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
# Post here is sotred as pydantic model and gets data from body for us using BaseModel
async def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 300000000000)
    my_posts.append(post_dict)

    print(my_posts)
    return {"message": "Post created successfully"}


@app.get("/api/posts/{id}")
async def get_post(id: int, response: Response):
    data_extract = find_post(id)

    if not data_extract:
        #     response.status_code = status.HTTP_404_NOT_FOUND
        #     return {"message": f"Post with id {id} not found"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found"
        )

    return {"data": data_extract}


@app.get("/api/posts")
async def get_all_posts():
    return {"data": my_posts}


@app.put("/api/posts/{id}")
async def update_posts(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict

    print(my_posts)

    return {"message": f"Updated Successfully"}


@app.delete("/api/posts/{id}")
async def delete_posts(id: int):
    index = find_index_post(id)
    my_posts.pop(index)

    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id{id} was not found",
        )

    return {"message": f"Post with id {id} deleted successfully"}


# ---------------------------------------------------------------------------------
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


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


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


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    # find the index in the array that has required ID
    # my_posts.pop(index)
    index = find_index_post(id)

    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    my_posts.pop(index)
    # when we use default 204 status, fastapi assumes if you deleted you should return data so message wont be printed
    # so use Response to send
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict

    return {"message": post_dict}
