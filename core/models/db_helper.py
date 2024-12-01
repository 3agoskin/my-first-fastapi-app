from asyncio import current_task
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

from core.config import settings


class DataBaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:  # type: ignore
        async with self.session_factory() as session:
            yield session  # type: ignore
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:  # type: ignore
        session = self.get_scoped_session()
        yield session  # type: ignore
        await session.close()


db_helper = DataBaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
