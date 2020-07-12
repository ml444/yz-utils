#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-6-30
@desc: ...
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .encoders import jsonable_encoder


@as_declarative()
class Base:
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Any
    __name__: str


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def count(self, db: Session, **kwargs):
        """
        获取总数
        :param db:
        :param kwargs:
        :return:
        """
        count = db.query(self.model).filter_by(**kwargs).count()
        return count

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        主键查询

        :param db:
        :param id:
        :return:
        """
        return db.query(self.model).get(id)

    def list(
            self, db: Session, *,
            opt: dict = None,
            sort: List[str] = None,
            offset: int = 0,
            limit: int = 100
    ) -> List[ModelType]:
        """
        列表查询

        :param db:
        :param opt:
        :param sort:
        :param offset:
        :param limit:
        :return:
        """
        if sort:
            sort = [text(s) for s in sort]
        if opt:
            return db.query(self.model).filter_by(
                **opt).order_by(sort).offset(offset).limit(limit).all()
        else:
            return db.query(self.model).order_by(sort).offset(
                offset).limit(limit).all()

    def create(
            self, db: Session, *,
            data: Union[Dict[str, Any], CreateSchemaType]
    ) -> ModelType:
        """
        插入操作

        :param db:
        :param data:
        :return:
        """
        if isinstance(data, BaseModel):
            data = jsonable_encoder(data)
        db_obj = self.model(**data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *,
            id: int = None,
            obj: ModelType = None,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            is_return_obj: bool = False
    ) -> ModelType:
        """
        更新操作

        :param db:
        :param id:
        :param obj:
        :param data:
        :param is_return_obj:
        :return:
        """
        if not any((id, obj)):
            raise ValueError('At least one of id or obj exists')
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.dict(exclude_unset=True)

        if not is_return_obj and id:
            update_count = db.query(self.model).filter(
                self.model.id == id).update(**update_data)
            db.commit()
            return update_count
        else:
            if not obj:
                obj = db.query(self.model).filter(
                    self.model.id == id).first()
            obj_data = jsonable_encoder(obj)

            for field in obj_data:
                if field in update_data:
                    setattr(obj, field, update_data[field])
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

    def delete(
            self, db: Session, *,
            id: int, is_return_obj: bool = False
    ) -> ModelType:
        """
        删除操作

        :param db:
        :param id:
        :param is_return_obj:
        :return:
        """
        if is_return_obj:
            obj = db.query(self.model).get(id)
            db.delete(obj)
            db.commit()
            return obj
        else:
            del_count = db.query(self.model).filter(
                self.model.id == id).delete()
            db.commit()
            return del_count
