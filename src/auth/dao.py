from .models import User, RefreshToken
from .schemas import UserCreateDB, UserUpdate, RefreshTokenCreate, RefreshTokenUpdate
from ..dao import BaseDAO


class UserDAO(BaseDAO[User, UserCreateDB, UserUpdate]):
    model = User


class RefreshTokenDAO(BaseDAO[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    model = RefreshToken