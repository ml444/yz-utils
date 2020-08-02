#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-6-30
@desc: ...
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
try:
    from sqlalchemy import text
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.declarative import as_declarative, declared_attr
except ModuleNotFoundError:
    print(f'''==> Warning: 
        if you need to use this module: {__file__}, 
        please: pip install sqlalchemy==1.3.16+''')
else:
    @as_declarative()
    class Base:
        # Generate __tablename__ automatically
        @declared_attr
        def __tablename__(cls) -> str:
            return cls.__name__.lower()

        id: Any
        __name__: str


from yz_utils.db.encoders import jsonable_encoder


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class FilterOptionError(Exception):
    """查询的过滤参数有误"""


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def count(self, db: Session, opt: Union[Dict, List] = None, **kwargs):
        """
        统计数量

        :param db:      数据库链接
        :param opt:     查询条件
        :param kwargs:  额外的查询条件
        :return:
        """
        if opt and isinstance(opt, dict):
            if kwargs:
                opt.update(kwargs)
            results = db.query(self.model).filter_by(**opt).count()
        elif opt and isinstance(opt, list):
            _opt = [text(s) for s in opt]
            if kwargs:
                results = db.query(self.model).filter(
                    *_opt).filter_by(**kwargs).count()
            else:
                results = db.query(self.model).filter(
                    *_opt).count()
        else:
            results = db.query(self.model).filter_by(**kwargs).count()
        return results

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
            opt: Union[Dict, List] = None,
            sort: List[str] = list(),
            offset: int = 0,
            limit: int = 10
    ) -> List[ModelType]:
        """
        列表查询

        :param db:
        :param opt:     查询条件
        :param sort:    排序条件
        :param offset:  选取的起点
        :param limit:   数量限度
        :return:
        """
        if sort:
            sort = [text(s) for s in sort]
        if opt and isinstance(opt, dict):
            return db.query(self.model).filter_by(
                **opt).order_by(*sort).offset(offset).limit(limit).all()
        elif opt and isinstance(opt, list):
            _opt = [text(s) for s in opt]
            return db.query(self.model).filter(
                *_opt).order_by(*sort).limit(limit).offset(offset).all()
        else:
            return db.query(self.model).order_by(*sort).offset(
                offset).limit(limit).all()

    def create(
            self, db: Session, *,
            data: Union[Dict[str, Any], CreateSchemaType]
    ) -> ModelType:
        """
        插入操作

        :param db:
        :param data: 创建时所需的数据
        :return:
        """
        if isinstance(data, BaseModel):
            data = jsonable_encoder(data)
        obj = self.model(**data)  # type: ignore
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(
            self, db: Session, *,
            id: int = None,
            obj: ModelType = None,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            is_return_obj: bool = False
    ) -> ModelType:
        """
        更新操作，id或者obj必须传入之一，传入obj时，更新后返回更新对象

        :param db:
        :param id: 需要更新的对象ID
        :param obj: 被更新的对象
        :param data: 需要更新的数据
        :param is_return_obj: 是否返回被更新的对象
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
        :param id: 需要删除的对象ID
        :param is_return_obj: 是否返回删除的对象
        :return:
        """
        if is_return_obj:
            obj = db.query(self.model).get(id)
            db.delete(obj)
            db.commit()
            return obj
        else:
            del_count = db.query(self.model).filter(
                self.model.id == id).delete(synchronize_session=False)
            db.commit()
            return del_count

    def batch_delete(self, ids: list, db: Session = None):
        """批量删除

        :param ids: 需要删除的对象ID列表
        :param db:
        :return:
        """
        deleted_count = db.query(self.model).filter(
            self.model.id.in_(ids)).delete(synchronize_session=False)
        # print(ids)
        # [db.delete(db.query(self.model).get(_id)) for _id in ids]
        # db.commit()
        return deleted_count

