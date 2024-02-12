import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


uniq_str_param = Annotated[str, mapped_column(nullable=False, unique=True)]
bool_param = Annotated[bool, mapped_column(default=False)]
datetime_tz_param = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())]


class User(Base):

    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email: Mapped[uniq_str_param]
    hashed_password: Mapped[uniq_str_param]
    username: Mapped[uniq_str_param]
    is_verified: Mapped[bool_param]
    is_active: Mapped[bool_param]
    is_superuser: Mapped[bool_param]
    created_at: Mapped[datetime_tz_param]
    

class RefreshToken(Base):
    
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[datetime_tz_param]
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"))