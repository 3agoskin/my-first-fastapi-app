from enum import Enum
from fastapi import FastAPI
import uvicorn

from items_views import router as items_router
from users.views import router as users_router


class RouterTag(Enum):
    ITEMS = "Items"
    USERS = "Users"


app = FastAPI()
app.include_router(items_router, tags=[RouterTag.ITEMS])
app.include_router(users_router, tags=[RouterTag.USERS])


@app.get("/")
def root():
    return {"message": "Root!"}


@app.get("/hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello, {name}!"}


@app.post("/calc/add")
def add(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
