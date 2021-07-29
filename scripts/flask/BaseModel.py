from sqlalchemy import create_engine
from sqlalchemy.orm import class_mapper, sessionmaker

from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime,date

from config.base_config import Config

Column = db.Column
relationship = db.relationship


class BaseModel(db.Model):
    __abstract__ = True

    default_json_fields = []

    @hybrid_property
    def updated_at(self):
        return self._updated_at.strftime('%Y-%m-%d %H:%M:%S') if self._updated_at else None

    @hybrid_property
    def created_at(self):
        return self._created_at.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self, child_num=None, fields=None, exclude=None):
        """
        将模型中的json_fields字段转化为JSON显示，判断如果是一对多关系显示子模型中的json_fields
        :param child_num: int
        :param fields: list
        :param exclude: list
        :return: dict
        """
        res = {}
        columns = [c.key for c in class_mapper(self.__class__).columns]
        if fields:
            columns = fields
        elif exclude:
            columns = [c for c in columns if c not in exclude]
        elif self.default_json_fields:
            columns = self.default_json_fields

        for k in columns:
            if k in self.__mapper__.relationships.keys():
                res[k] = []
                for c in getattr(self, k)[:child_num]:
                    res[k].append(c.to_json())
            else:
                val = getattr(self, k)
                if isinstance(val, datetime):
                    res[k] = val.strftime('%Y-%m-%d %X')
                elif isinstance(val, date):
                    res[k] = val.strftime('%Y-%m-%d')
                else:
                    res[k] = val
        return res

    @classmethod
    def get(cls, num=None, child_num=None):
        """
        :param num: int or str('all')
        :param child_num: int
        :return: array
        """
        items = cls.get_item(num)
        return [item.to_json(child_num) for item in items]

    @classmethod
    def get_item(cls, num=None):
        """
        执行模型查询，有排序字段时加入排序字段进行查询
        :param num: int or str('all'), if None means 1
        :return: list
        """
        if hasattr(cls, 'order'):
            order = 'order'
        else:
            order = 'updated_at'

        if num is 'all':
            items = cls.query.order_by(order).all()
            return items
        elif num is None:
            num = 1
        items = cls.query.order_by(order)[:num]
        return items

    @classmethod
    def create(cls, commit=True, **kwargs,):
        """Create a new record and save it """
        instance = cls(**kwargs)
        return instance.save(commit)

    def update(self, commit=True, **kwargs):
        """Update an exist record and save it """
        for attr, value in kwargs.items():
            try:  # 部分属性无法setattr，例如hybird
                setattr(self, attr, value)
            except:
                pass
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record to database."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


def get_session(path=Config.SQLALCHEMY_BINDS['master_pyvboard']):
    """
    获取数据库会话连接
    :param path 数据库连接地址 'mysql://root:password@host:port/db?charset=utf8'
    """
    engine = create_engine(path, pool_size=10, pool_recycle=7200,
                           pool_pre_ping=True, encoding='utf-8')
    session = sessionmaker(bind=engine)
    return session()
