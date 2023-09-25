from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from fastapi.params import Body
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time

app = FastAPI()

# Database psycopg is like jdbc driver for java
# until the db connection is established, no api is available
while True:
    try:
        conn = psycopg.connect(
            host="localhost",
            dbname="fastapi_sanjeev",
            user="postgres",
            password="password",
            row_factory=dict_row,  # only for version 3 of psycopg
        )
        cursor = conn.cursor()
        print("Database connection was established!")
        break
    except Exception as error:
        print("Failed to connect to Database!")
        print("Error was: ", error)
        time.sleep(2)


# pydantic validation
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
# Post here is sotred as pydantic model and gets data from body for us using BaseModel
async def create_post(post: Post):
    # this %s will prevent sql injection
    cursor.execute(
        """ INSERT INTO posts(title,content,published) VALUES (%s,%s,%s)  RETURNING * """,
        (post.title, post.content, post.published),
    )

    # just to get returning wala value we cant get up there
    new_post = cursor.fetchone()

    # for persistent
    conn.commit()
    return {"message": f"Post created successfully {new_post}"}


@app.get("/api/posts/{id}")
async def get_post(id: int, response: Response):
    # because sql query is string we need to convert id to str too
    # i passed , comma after id because
    # The error you're encountering in your SQL query is likely related to how you're passing the id parameter to the query. When using the %s placeholder for parameters
    #  in SQL queries, you should pass a tuple or a list as the second argument to execute(). In your code, you're passing str(id) as a single value, which is causing the error.
    cursor.execute(""" SELECT * FROM Posts where id = %s """, (str(id),))
    data_extract = cursor.fetchone()

    print(data_extract)

    if not data_extract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found"
        )

    return {"data": data_extract}


@app.get("/api/posts")
async def get_all_posts():
    cursor.execute(""" SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.put("/api/posts/{id}")
async def update_posts(id: int, post: Post):
    cursor.execute(
        """ UPDATE posts SET title = %s, content = %s, published =%s where id = %s returning * """,
        (post.title, post.content, post.published, str(id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    return {"message": f"Updated Successfully {updated_post}"}


@app.delete("/api/posts/{id}")
async def delete_posts(id: int):
    cursor.execute(""" DELETE FROM posts where id = %s  returning *""", ((str(id)),))

    deleted_data = cursor.fetchone()
    conn.commit()

    if deleted_data == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    return {"message": f"Post with id {id} deleted successfully"}
