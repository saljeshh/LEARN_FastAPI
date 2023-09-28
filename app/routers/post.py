from fastapi import HTTPException, Response, status, Depends, APIRouter
import models
import schemas
from sqlalchemy.orm import Session
from database import get_db
from typing import List
import oauth2
from typing import Optional


router = APIRouter(prefix="/api/posts", tags=["Posts"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,  # for response pydanctic model
)
# Post here is sotred as pydantic model and gets data from body for us using BaseModel
# depends is dependency
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
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

    print(current_user.email)

    # print(post.model_dump())
    # print(**post.model_dump()) # this will throw type error as print cant print kwargs

    # we just unpacked dict so that we dont need to do title = post.title ....
    new_post = models.Post(**post.model_dump())
    # .Post is nothing but model

    # new post is now sql alchemy model .. so to make sure it works for response we need to asdd class config in schemas.. see there

    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # it is doing returning * like sql
    # return {"message": f"Post created successfully"}
    return new_post


@router.get("/{id}")
async def get_post(
    id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
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

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    # return {"data": post}
    return post


# if we dont keep that typing.List[schemas.Post] we are returning multiople post but we will only be returning one Post schema so it gives error
@router.get("/", response_model=List[schemas.Post])
async def get_all_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # ----------- if i want to only get users specific all posts like for expense tracker
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    # offset means skip

    print(limit)
    # using alchemy
    # posts = db.query(models.Post).all()
    # return {"data": posts}
    # authomatically serialize and just send data not posts: [{},{}]
    return posts


@router.put("/{id}")
async def update_posts(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
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

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    # chaining update
    post_query.update(post.model_dump())
    db.commit()

    return {"message": f"Updated Successfully"}


@router.delete("/{id}")
async def delete_posts(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" DELETE FROM posts where id = %s  returning *""", ((str(id)),))

    # deleted_data = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete()
    db.commit()

    return {"message": f"Post with id {id} deleted successfully"}
