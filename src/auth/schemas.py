from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_superuser: bool = Field(False)
    is_active: bool = Field(True)
    is_verified: bool = Field(False)
    
class UserCreate(UserBase):
    password: str 

class UserCreateDB(UserBase):
    hashed_password: str 

class UserGet(UserBase):
    id: UUID
    email: EmailStr
    username: str
    is_superuser: bool
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True
        
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    hashed_password: str | None = None
    is_verified: bool | None = None
    is_superuser: bool | None = None
    

class RefreshTokenCreate(BaseModel):
    refresh_token: UUID
    expires_in: int
    user_id: UUID

class RefreshTokenUpdate(RefreshTokenCreate):
    user_id: str | None = Field(None)
    

class Token(BaseModel):
    access_token: str
    refresh_token: UUID
    token_type: str
    
    
class LoginResponse(BaseModel):
    user: UserGet
    tokens: Token