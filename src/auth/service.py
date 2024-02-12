import uuid
import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_

from . import schemas, models, exceptions, utils
from .dao import UserDAO, RefreshTokenDAO

from ..config import settings



class UserService:
    
    @classmethod
    async def create_user(cls, user: schemas.UserCreate) -> models.User:
        
        await cls.__check_if_user_exists(username=user.username, email=user.email)
        
        return await cls.__create_db_user(user=user)
    
    @staticmethod
    async def __create_db_user(user: schemas.UserCreate) -> models.User:
        
        hashed_password = await utils.get_hashed_password(user.password)
        
        return await UserDAO.add(
            schemas.UserCreateDB(
                **user.model_dump(),
                id=id,
                hashed_password=hashed_password
            )
        )
        
    @staticmethod
    async def __check_if_user_exists(username: str, email: str) -> None:
        
        if await UserDAO.find_all(or_(models.User.username == username, models.User.email == email)):
            raise exceptions.UserAlreadyExists

    @classmethod
    async def get_user(cls, user_id: uuid.UUID = None, token: str = None, username: str = None) -> models.User:
        
        if not user_id and not token and not username:
            raise exceptions.NoUserData
        
        if token:
            user_id = await cls._get_access_token_payload(access_token=token)
        
        return await UserDAO.find_one_or_none(or_(models.User.id == user_id, models.User.username == username))
    
    @classmethod
    async def get_all_users(cls, *filter, offset: int, limit: int, **filter_by) -> list[models.User]:

        return await UserDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)

    @classmethod
    async def set_superuser(cls, access_token: str, user_id: str) -> dict:
        
        superuser = await cls.get_user(token=access_token)
        
        if superuser.is_superuser:
            
            user = await cls.get_user(user_id=user_id)     
            if not user:
                raise exceptions.UserDoesNotExist
            
            await UserDAO.update(models.User.id==user.id, obj_in={"is_superuser": not(user.is_superuser)})
            
            return {"Message": f"User {user_id} now has superuser status: {not(user.is_superuser)}"}
        
        raise exceptions.Forbidden
    
    @classmethod
    async def delete_user(cls, user_id: uuid.UUID) -> dict:
        
        db_user = await UserDAO.find_one_or_none(id=user_id)
        if db_user is None:
            raise exceptions.UserDoesNotExist
        
        await UserDAO.update(models.User.id == user_id, obj_in={'is_active': False})
        return {"Message": f"User {user_id} was deleted successfuly"}
    
    @classmethod
    async def delete_user_from_superuser(cls, token: str, user_id: uuid.UUID):
        
        superuser_id = await cls._get_access_token_payload(access_token=token)
        superuser = await cls.get_user(user_id=superuser_id)
        if superuser.is_superuser:    
            await UserDAO.delete(models.User.id == user_id)
            return {"Message": f"Superuser {superuser_id} deleted {user_id} successfuly"}
        
        raise exceptions.Forbidden
    
    @staticmethod
    async def _get_access_token_payload(access_token: str):
        try:
            payload = jwt.decode(access_token,settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            return user_id

        except jwt.ExpiredSignatureError as e:
            raise exceptions.TokenExpired

        except jwt.DecodeError as e:
            raise exceptions.InvalidToken
    
    
class AuthService:
    
    @classmethod
    async def create_tokens(cls, user_id: uuid.UUID) -> schemas.Token:
        access_token = await cls.__create_access_token(user_id=user_id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await cls.__create_refresh_token()

        await RefreshTokenDAO.add(
            schemas.RefreshTokenCreate(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds()
            )
        )
        return schemas.Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    
    @staticmethod
    async def __create_access_token(user_id: uuid.UUID, **kwargs) -> str:

        to_encode = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        to_encode.update(**kwargs)
        encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

        return f'Bearer {encoded_jwt}'
    
    @classmethod
    async def __create_refresh_token(cls) -> uuid.UUID:
        return uuid.uuid4()
    
    @classmethod
    async def refresh_token(cls, token: uuid.UUID) -> schemas.Token:
        
        refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
        if refresh_token is None:
            raise exceptions.InvalidToken
        
        if datetime.now(timezone.utc) >= refresh_token.created_at + timedelta(seconds=refresh_token.expires_in):
            await RefreshTokenDAO.delete(id=refresh_token.id)
            raise exceptions.TokenExpired
        
        user = await UserDAO.find_one_or_none(id=refresh_token.user_id)
        if user is None:
            raise exceptions.InvalidToken
        
        access_token = await cls.__create_access_token(user.id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = await cls.__create_refresh_token()
        
        await RefreshTokenDAO.update(
            models.RefreshToken.id == refresh_token.id,
            obj_in=schemas.RefreshTokenUpdate(
                refresh_token=new_refresh_token,
                expires_in=refresh_token_expires.total_seconds()
            )
        )
        
        return schemas.Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")
    
    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> models.User:
        
        user = await UserDAO.find_one_or_none(username=username)
        if user and await utils.validate_password(password, user.hashed_password):
            return user
        
        raise exceptions.InvalidAuthenthicationCredential
    
    @classmethod
    async def logout(cls, token: uuid.UUID) -> dict:
        
        refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
        if refresh_token:
            await RefreshTokenDAO.delete(id=refresh_token.id)
        
        return {"Message": "logout was successful"}
    
    @classmethod
    async def abort_all_sessions(cls, user_id: uuid.UUID):
        await RefreshTokenDAO.delete(models.RefreshToken.user_id == user_id)
        
        return {"Message": f"Aborting all user {user_id} sessions was successful"}

