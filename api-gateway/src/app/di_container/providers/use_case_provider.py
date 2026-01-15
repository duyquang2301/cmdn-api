"""Use case provider for DI container."""

from dishka import Provider, Scope, provide

from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.model.task.task_repository import TaskRepository
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.audio_analyzer.audio_analyzer import AudioAnalyzer
from app.domain.support.file_storage.file_storage import FileStorage
from app.domain.support.logger.logger import Logger
from app.domain.support.task_queue.task_queue import TaskQueue
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.use_case.create_meeting_use_case import CreateMeetingUseCase
from app.use_case.create_user_use_case import CreateUserUseCase
from app.use_case.delete_meeting_use_case import DeleteMeetingUseCase
from app.use_case.find_many_task_use_case import FindManyTaskUseCase
from app.use_case.find_meeting_list_use_case import FindMeetingListUseCase
from app.use_case.find_meeting_status_use_case import FindMeetingStatusUseCase
from app.use_case.find_meeting_use_case import FindMeetingUseCase
from app.use_case.update_meeting_use_case import UpdateMeetingUseCase
from app.use_case.upload_audio_use_case import UploadAudioUseCase


class UseCaseProvider(Provider):
    """Provider for application use cases."""

    scope = Scope.REQUEST

    @provide
    def provide_create_meeting_use_case(
        self,
        meeting_repository: MeetingRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> CreateMeetingUseCase:
        """Provide create meeting use case."""
        return CreateMeetingUseCase(
            meeting_repository=meeting_repository,
            transaction_manager=transaction_manager,
            logger=logger,
        )

    @provide
    def provide_find_meeting_use_case(
        self,
        meeting_repository: MeetingRepository,
        user_repository: UserRepository,
        logger: Logger,
    ) -> FindMeetingUseCase:
        """Provide find meeting use case."""
        return FindMeetingUseCase(
            meeting_repository=meeting_repository,
            user_repository=user_repository,
            logger=logger,
        )

    @provide
    def provide_find_meeting_list_use_case(
        self,
        meeting_repository: MeetingRepository,
        user_repository: UserRepository,
        logger: Logger,
    ) -> FindMeetingListUseCase:
        """Provide find meeting list use case."""
        return FindMeetingListUseCase(
            meeting_repository=meeting_repository,
            user_repository=user_repository,
            logger=logger,
        )
        return FindMeetingListUseCase(
            meeting_repository=meeting_repository,
            logger=logger,
        )

    @provide
    def provide_update_meeting_use_case(
        self,
        meeting_repository: MeetingRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> UpdateMeetingUseCase:
        """Provide update meeting use case."""
        return UpdateMeetingUseCase(
            meeting_repository=meeting_repository,
            transaction_manager=transaction_manager,
            logger=logger,
        )

    @provide
    def provide_delete_meeting_use_case(
        self,
        meeting_repository: MeetingRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> DeleteMeetingUseCase:
        """Provide delete meeting use case."""
        return DeleteMeetingUseCase(
            meeting_repository=meeting_repository,
            transaction_manager=transaction_manager,
            logger=logger,
        )

    @provide
    def provide_find_meeting_status_use_case(
        self,
        meeting_repository: MeetingRepository,
        logger: Logger,
    ) -> FindMeetingStatusUseCase:
        """Provide find meeting status use case."""
        return FindMeetingStatusUseCase(
            meeting_repository=meeting_repository,
            logger=logger,
        )

    @provide
    def provide_upload_audio_use_case(
        self,
        audio_analyzer: AudioAnalyzer,
        file_storage: FileStorage,
        meeting_repository: MeetingRepository,
        user_repository: UserRepository,
        task_queue: TaskQueue,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> UploadAudioUseCase:
        """Provide upload audio use case."""
        return UploadAudioUseCase(
            audio_analyzer=audio_analyzer,
            file_storage=file_storage,
            meeting_repository=meeting_repository,
            user_repository=user_repository,
            task_queue=task_queue,
            transaction_manager=transaction_manager,
            logger=logger,
        )

    @provide
    def provide_find_many_task_use_case(
        self,
        task_repository: TaskRepository,
        logger: Logger,
    ) -> FindManyTaskUseCase:
        """Provide find many task use case."""
        return FindManyTaskUseCase(
            task_repository=task_repository,
            logger=logger,
        )

    @provide
    def provide_create_user_use_case(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> CreateUserUseCase:
        """Provide create user use case."""
        return CreateUserUseCase(
            user_repository=user_repository,
            transaction_manager=transaction_manager,
            logger=logger,
        )
