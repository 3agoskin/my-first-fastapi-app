from fastapi import APIRouter
from users import crud
from users.schemas import CreateUser


router = APIRouter(prefix="/users")


@router.post("/")
def create_user(user: CreateUser): # body not needed any more, FastAPI understand that is json object now
    return crud.create_user(user_in=user )
