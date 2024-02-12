from typing import Optional, Union
from fastapi import APIRouter, status, Depends
from pydantic import BaseModel

from . import models, schemas
from .service import UserService, AuthService


auth_router = APIRouter(prefix="/auth")
user_router = APIRouter(prefix="/users")


@auth_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    user: schemas.UserCreate
) -> schemas.UserGet:
    return await UserService.create_user(user)


@auth_router.post("/login")
async def login(
    username: str, 
    password: str
) -> schemas.LoginResponse:
    user = await AuthService.authenticate_user(username, password)
    tokens = await AuthService.create_tokens(user.id)

    return {"user": user, "tokens": tokens}


@auth_router.post("/logout")
async def logout(
    token: str,
): 
    return await AuthService.logout(token)


@auth_router.put("/refresh_token")
async def refresh_token(
    token: str,
) -> schemas.Token:
    return await AuthService.refresh_token(token)


@auth_router.delete("/abort_all_sessions")
async def abort_all_sessions(
    user_id: str, 
):
    return await AuthService.abort_all_sessions(user_id)


@user_router.get("/get_user")
async def get_user(
    token: str = None,
    user_id: str = None,
) -> schemas.UserGet:

    return await UserService.get_user(token=token, user_id=user_id)

@user_router.get("/get_all_users")
async def get_all_users(
    offset: Optional[int] = 0,
    limit: Optional[int] = 100,
    is_active: bool = True,
) -> list[schemas.UserGet]:
    return await UserService.get_all_users(is_active=is_active, offset=offset, limit=limit)

@user_router.patch("/set_superuser")
async def set_super_user(
    token: str,
    user_id: str,    
):
    return await UserService.set_superuser(access_token=token, user_id=user_id)


@user_router.delete("/delete_user")
async def delete_user(
    user_id: str,
):

    return await UserService.delete_user(user_id=user_id)

@user_router.delete("/delete_user_from_superuser")
async def delete_user_from_superuser(
    token: str,
    user_id: str,
):

    return await UserService.delete_user_from_superuser(user_id=user_id, token=token)