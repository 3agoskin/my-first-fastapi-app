import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])


security = HTTPBasic()


@router.get(path="/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return {
        "message": "hi!",
        "username": credentials.username,
        "password": credentials.password,
    }


usernames_to_password = {
    "admin": "admin",
    "john": "password",
}


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

    correct_password = usernames_to_password.get(credentials.username)

    if correct_password is None:
        raise unauth_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauth_exc

    return credentials.username


@router.get(path="/basic-auth-username/")
def demo_basic_auth_username(auth_username: str = Depends(get_auth_user_username)):
    return {
        "message": f"Hello, {auth_username}!",
        "username": auth_username,
    }
