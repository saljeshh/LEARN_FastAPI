from fastapi import FastAPI
import models
from database import engine
from routers import post
from routers import user
from routers import auth
from config import settings


print(settings.database_username)

# creates all table of models for us
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
