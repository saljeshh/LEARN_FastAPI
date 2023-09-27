from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.params import Body
from random import randrange
import time
import models
import schemas
from sqlalchemy.orm import Session
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Database psycopg is like jdbc driver for java
# until the db connection is established, no api is available
while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi_sanjeev",
            user="postgres",
            password="password",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was established!")
        break
    except Exception as error:
        print("Failed to connect to Database!")
        print("Error was: ", error)
        time.sleep(2)


# only for testing purpose
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    # print(db.query(models.Post))  # give select query select * from table
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.post(
    "/api/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,  # for response pydanctic model
)
# Post here is sotred as pydantic model and gets data from body for us using BaseModel
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # this %s will prevent sql injection
    # cursor.execute(
    #     """ INSERT INTO posts(title,content,published) VALUES (%s,%s,%s)  RETURNING * """,
    #     (post.title, post.content, post.published),
    # )

    # # just to get returning wala value we cant get up there
    # new_post = cursor.fetchone()

    # # for persistent
    # conn.commit()

    # Using Alchemy---------------------

    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )

    print(post.model_dump())
    # print(**post.model_dump()) # this will throw type error as print cant print kwargs

    # we just unpacked dict so that we dont need to do title = post.title ....
    new_post = models.Post(**post.model_dump())

    # new post is now sql alchemy model .. so to make sure it works for response we need to asdd class config in schemas.. see there

    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # it is doing returning * like sql
    # return {"message": f"Post created successfully"}
    return new_post


@app.get("/api/posts/{id}")
async def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    # because sql query is string we need to convert id to str too
    # i passed , comma after id because
    # The error you're encountering in your SQL query is likely related to how you're passing the id parameter to the query. When using the %s placeholder for parameters
    #  in SQL queries, you should pass a tuple or a list as the second argument to execute(). In your code, you're passing str(id) as a single value, which is causing the error.

    # cursor.execute(""" SELECT * FROM Posts where id = %s """, (str(id),))
    # data_extract = cursor.fetchone()

    # print(data_extract)

    # Using Alchemy
    post = (
        db.query(models.Post).filter(models.Post.id == id).first()
    )  # first is to make efficient stop searching after found one
    print(post)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found"
        )

    # return {"data": post}
    return post


# if we dont keep that typing.List[schemas.Post] we are returning multiople post but we will only be returning one Post schema so it gives error
@app.get("/api/posts", response_model=List[schemas.Post])
async def get_all_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # using alchemy
    posts = db.query(models.Post).all()
    # return {"data": posts}
    # authomatically serialize and just send data not posts: [{},{}]
    return posts


@app.put("/api/posts/{id}")
async def update_posts(
    id: int, post: schemas.PostCreate, db: Session = Depends(get_db)
):
    # cursor.execute(
    #     """ UPDATE posts SET title = %s, content = %s, published =%s where id = %s returning * """,
    #     (post.title, post.content, post.published, str(id)),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post_database = post_query.first()

    if post_database == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    # chaining update
    post_query.update(post.model_dump())
    db.commit()

    return {"message": f"Updated Successfully"}


@app.delete("/api/posts/{id}")
async def delete_posts(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" DELETE FROM posts where id = %s  returning *""", ((str(id)),))

    # deleted_data = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post.delete(synchronize_session=False)
    db.commit()

    return {"message": f"Post with id {id} deleted successfully"}
