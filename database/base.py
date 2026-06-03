import logging
from typing import Optional, Any

from sqlalchemy import BigInteger, select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, sessionmaker

from config import conf


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__[:1]
        for i in cls.__name__[1:]:
            if i.isupper():
                name += '_'
            name += i
        name = name.lower()
        if name.endswith('y'):
            name = name[:-1] + 'ie'
        return name.lower() + 's'

    __abstract__ = True


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(conf.database.db_url)
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession()
db.init()


class AbstractBase:
    id = None
    telegram_id = None
    name = None

    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            logging.info(f'rollback error: {e}')

    @classmethod
    async def create(cls, **kwargs: Any):
        obj = cls(**kwargs)
        db.add(obj)
        await db.commit()
        return obj

    @classmethod
    async def update(cls, _id: Optional[int] = None, **kwargs):
        regular_kwargs = {k: v for k, v in kwargs.items()}
        if regular_kwargs:
            query = sql_update(cls).where(cls.id == _id).values(**regular_kwargs).execution_options(
                synchronize_session='fetch')

            await db.execute(query)

        await cls.commit()

    @classmethod
    async def get(cls, _id: int):
        return (await db.execute(select(cls).where(cls.id == _id))).scalar()

    @classmethod
    async def get_all(cls):
        return (await db.execute(select(cls))).scalars().all()


class BaseModel(Base, AbstractBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
