from enum import Enum
from users.schemas import CreateUser


class Status(Enum):
    SUCCESS = "success"
    FAIL = "fail"


def create_user(user_in: CreateUser) -> dict[str, Status | CreateUser]:
    new_user = user_in.model_dump()
    print(new_user)
    return {
        "message": Status.SUCCESS,
        "user": user_in,
    }
