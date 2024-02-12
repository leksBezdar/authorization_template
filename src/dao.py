from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from fastapi import HTTPException
from loguru import logger

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from .database import Base, async_session_maker


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    @classmethod
    async def add(
        cls,
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:

        async with async_session_maker() as db: 
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump(exclude_unset=True)

            try:
                stmt = insert(cls.model).values(
                    **create_data).returning(cls.model)
                result = await db.execute(stmt)
                await db.commit()
                return result.scalars().first()
            except (SQLAlchemyError, Exception) as e:
                print(e)

                logger.error(e)

                if isinstance(e, SQLAlchemyError):
                    msg = "Database Exc: Cannot insert data into table"
                    raise HTTPException(status_code=500, detail=msg)

                elif isinstance(e, Exception):
                    msg = "Unknown Exc: Cannot insert data into table"
                raise HTTPException(status_code=500, detail=msg)


    @classmethod
    async def find_one_or_none(cls, *filter, **filter_by) -> Optional[ModelType]:

        async with async_session_maker() as db: 

            stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
            result = await db.execute(stmt)

            return result.scalars().one_or_none()

    @classmethod
    async def find_all(
        cls,
        *filter,
        offset: int | None = None,
        limit: int | None = None,
        **filter_by
    ) -> List[ModelType]:

        async with async_session_maker() as db: 

            stmt = (
                select(cls.model)
                .filter(*filter)
                .filter_by(**filter_by)
                .offset(offset)
                .limit(limit)
            )
            result = await db.execute(stmt)
            return result.scalars().all()

    @classmethod
    async def update(
        cls,
        *where,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        
        async with async_session_maker() as db: 
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            stmt = (
                update(cls.model).
                where(*where).
                values(**update_data).
                returning(cls.model)
            )
            
            result = await db.execute(stmt)
            await db.commit()
            return result.scalars().one()

    @classmethod
    async def delete(cls,  *filter, **filter_by) -> None:
        async with async_session_maker() as db: 
            stmt = delete(cls.model).filter(*filter).filter_by(**filter_by)
            await db.execute(stmt)
            await db.commit()
            