import secrets
import time
from typing import Annotated, Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
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
def demo_basic_auth_username(
    auth_username: str = Depends(get_auth_user_username),
):
    return {
        "message": f"Hello, {auth_username}!",
        "username": auth_username,
    }


static_auth_token_to_username = {
    "54cde5389311f2112e0c976bf86533a2": "admin",
    "288914f057891b60d4af3b9cf0d3af87": "john",
}


def get_auth_username_by_static_auth_token(
    static_token: str = Header(alias="x-auth-token"),
) -> str:
    if static_token not in static_auth_token_to_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )

    return static_auth_token_to_username[static_token]


@router.get(path="/some-http-header-auth/")
def demo_auth_some_http_header(
    username: str = Depends(get_auth_username_by_static_auth_token),
):
    return {
        "message": f"Hello, {username}!",
        "username": username,
    }


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


@router.post(path="/login-cookie/")
def demo_auth_login_cookie(
    response: Response,
    auth_username: str = Depends(get_auth_username_by_static_auth_token),
):
    session_id = generate_session_id()
    COOKIES[session_id] = {
        "username": auth_username,
        "login_at": int(time.time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}


def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
) -> dict[str, Any]:
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return COOKIES[session_id]


@router.get(path="/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict[str, Any] = Depends(get_session_data)
):
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}!",
        **user_session_data,
    }


@router.get(path="/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict[str, Any] = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }
