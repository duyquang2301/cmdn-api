"""Infrastructure layer provider for DI container."""

from collections.abc import AsyncIterator
from typing import Any

import aioboto3
from celery import Celery
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.di_container.settings import settings
from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.model.task.task_repository import TaskRepository
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.file_storage.file_storage import FileStorage
from app.domain.support.logger.logger import Logger
from app.domain.support.task_queue.task_queue import TaskQueue
from app.infrastructure.db_client.flusher import Flusher
from app.infrastructure.db_client.flusher_impl import FlusherImpl
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.infrastructure.db_client.transaction_manager_impl import TransactionManagerImpl
from app.infrastructure.file_storage.s3_storage_impl import S3StorageImpl
from app.infrastructure.persistence.repository.meeting_repository_impl import (
    MeetingRepositoryImpl,
)
from app.infrastructure.persistence.repository.task_repository_impl import (
    TaskRepositoryImpl,
)
from app.infrastructure.persistence.repository.user_repository_impl import (
    UserRepositoryImpl,
)
from app.infrastructure.task_queue.celery_queue_impl import CeleryQueueImpl


class InfrastructureProvider(Provider):
    """Provider for infrastructure layer components."""

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        """Provide async database engine singleton."""
        return create_async_engine(
            str(settings.database.url),
            echo=settings.database.echo,
            echo_pool=settings.database.echo_pool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,
        )

    @provide(scope=Scope.APP)
    def provide_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Provide async session factory singleton."""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        """Provide async database session per request."""
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_meeting_repository(self, session: AsyncSession) -> MeetingRepository:
        """Provide meeting repository."""
        return MeetingRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def provide_task_repository(self, session: AsyncSession) -> TaskRepository:
        """Provide task repository."""
        return TaskRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def provide_user_repository(self, session: AsyncSession) -> UserRepository:
        """Provide user repository."""
        return UserRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def provide_flusher(self, session: AsyncSession) -> Flusher:
        """Provide flusher for database operations."""
        return FlusherImpl(session)

    @provide(scope=Scope.REQUEST)
    def provide_transaction_manager(self, session: AsyncSession) -> TransactionManager:
        """Provide transaction manager."""
        return TransactionManagerImpl(session)

    @provide(scope=Scope.APP)
    def provide_s3_session(self) -> aioboto3.Session:
        """Provide S3 session singleton."""
        return aioboto3.Session(
            aws_access_key_id=settings.s3.access_key_id,
            aws_secret_access_key=settings.s3.secret_access_key,
            region_name=settings.s3.region,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_s3_client(
        self, s3_session: aioboto3.Session
    ) -> AsyncIterator[Any]:
        """Provide S3 client with automatic cleanup."""
        client_kwargs: dict[str, Any] = {"service_name": "s3"}
        if settings.s3.endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3.endpoint_url

        async with s3_session.client(**client_kwargs) as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def provide_file_storage(self, s3_client: Any, logger: Logger) -> FileStorage:
        """Provide file storage service."""
        return S3StorageImpl(
            client=s3_client,
            bucket_name=settings.s3.bucket_name,
            region=settings.s3.region,
            endpoint_url=settings.s3.endpoint_url,
            logger=logger,
        )

    @provide(scope=Scope.APP)
    def provide_celery_app(self) -> Celery:
        """Provide Celery app singleton."""
        return Celery(
            "audio_transcription",
            broker=settings.rabbitmq.broker_url,
            backend=settings.redis.url,
        )

    @provide(scope=Scope.APP)
    def provide_task_queue(self, celery_app: Celery, logger: Logger) -> TaskQueue:
        """Provide task queue service."""
        return CeleryQueueImpl(
            celery_app=celery_app,
            logger=logger,
        )
