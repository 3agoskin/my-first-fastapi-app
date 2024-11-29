from contextlib import asynccontextmanager
from enum import Enum
from fastapi import FastAPI
import uvicorn

from core.config import settings
from api_v1 import router as router_v1
from items_views import router as items_router
from users.views import router as users_router


class RouterTag(Enum):
    ITEMS = "Items"
    USERS = "Users"


@asynccontextmanager
async def lifespan(app: FastAPI):


    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.include_router(items_router, tags=[RouterTag.ITEMS])
app.include_router(users_router, tags=[RouterTag.USERS])


@app.get("/")
def root():
    return {"message": "Root!"}

@app.post("/img/")
def recive_img():
    pass


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
