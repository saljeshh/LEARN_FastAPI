from fastapi import Body, FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/posts")
async def get_posts():
    return {"data": "This is your first post!"}


@app.post("/createposts")
# extract all data from req body, type cast to dict and store in payload
async def create_post(payload: dict = Body(...)):
    return {
        "message": f"You did {payload['type']} from {payload['account']} account on {payload['date']} amount of {payload['amount']}"
    }
