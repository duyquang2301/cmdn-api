"""Upload audio use case."""

from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID, uuid4

from app.domain.model.meeting.meeting import Meeting
from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.model.user.user import User
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.audio_analyzer.audio_analyzer import AudioAnalyzer
from app.domain.support.file_storage.file_storage import FileStorage
from app.domain.support.logger.logger import Logger
from app.domain.support.task_queue.task_queue import TaskQueue
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.util.enums.status import Status
from app.util.exceptions import QuotaExceededError
from app.util.result import Result, failure, success


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadAudioUseCaseInput:
    """Input for upload audio use case."""

    file: BinaryIO
    filename: str
    content_type: str
    auth0_user_id: str
    title: str | None = None
    email: str | None = None


@dataclass(frozen=True, slots=True)
class UploadAudioUseCaseOutput:
    """Output for upload audio use case."""

    meeting_id: UUID
    audio_url: str
    task_id: str


class UploadAudioUseCase:
    """Upload audio and create meeting use case."""

    def __init__(
        self,
        *,
        file_storage: FileStorage,
        meeting_repository: MeetingRepository,
        user_repository: UserRepository,
        task_queue: TaskQueue,
        transaction_manager: TransactionManager,
        audio_analyzer: AudioAnalyzer,
        logger: Logger,
    ) -> None:
        self._file_storage = file_storage
        self._meeting_repository = meeting_repository
        self._user_repo = user_repository
        self._task_queue = task_queue
        self._transaction_manager = transaction_manager
        self._audio_analyzer = audio_analyzer
        self._logger = logger

    async def execute(
        self, input: UploadAudioUseCaseInput
    ) -> Result[UploadAudioUseCaseOutput, Exception]:
        meeting_id = uuid4()
        self._logger.info(f"Upload started: {meeting_id}, {input.filename}")

        try:
            # Validate audio and quota
            validation_result = await self._validate_audio_and_quota(
                input.file, input.filename, input.auth0_user_id
            )
            if not validation_result.success:
                return validation_result

            duration_seconds, user = validation_result.data

            # Upload file
            upload_result = await self._file_storage.upload_file(
                file=input.file,
                filename=input.filename,
                content_type=input.content_type,
            )
            if not upload_result.success:
                return failure(upload_result.error)
            audio_url = upload_result.data

            # Create meeting
            meeting = Meeting.create(
                id=meeting_id,
                title=input.title or f"Meeting {meeting_id}",
                description=None,
                audio_url=audio_url,
                duration=duration_seconds,
                user_id=user.id,
                status=Status.PROCESSING,
            )

            # Save meeting and update quota
            save_result = await self._save_meeting_and_update_quota(
                meeting, user, duration_seconds
            )
            if not save_result.success:
                return save_result

            # Send transcribe task
            task_result = self._task_queue.send_transcribe_task(meeting.id, audio_url)
            task_id = task_result.data if task_result.success else "failed"

            self._logger.info(f"Upload completed: {meeting.id}, {duration_seconds}s")

            return success(
                UploadAudioUseCaseOutput(
                    meeting_id=meeting.id,
                    audio_url=audio_url,
                    task_id=task_id,
                )
            )

        except Exception as e:
            self._logger.error(f"Upload failed: {e}")
            await self._transaction_manager.rollback()
            return failure(e)

    async def _validate_audio_and_quota(
        self, file: BinaryIO, filename: str, auth0_user_id: str
    ) -> Result[tuple[float, User], Exception]:
        """Validate audio duration and user quota."""
        # Validate audio (includes format, size, and duration validation)
        duration = await self._audio_analyzer.detect_duration(
            file=file, filename=filename
        )
        duration_seconds = float(duration)

        # Validate quota
        user_result = await self._user_repo.find_by_auth0_id(auth0_user_id)
        if not user_result.success or user_result.data is None:
            return failure(ValueError(f"User not found: {auth0_user_id}"))
        user = user_result.data

        quota_limit = user.get_daily_quota_seconds()
        if quota_limit is not None:
            new_total = user.used_duration_seconds + duration_seconds
            if new_total > quota_limit:
                remaining = max(0, quota_limit - user.used_duration_seconds)
                return failure(
                    QuotaExceededError(
                        message=(
                            f"Quota exceeded. Used: {user.used_duration_seconds / 3600:.1f}h / "
                            f"{quota_limit / 3600:.1f}h. Remaining: {remaining / 60:.0f}m. "
                            f"Requested: {duration_seconds / 60:.0f}m."
                        ),
                        used_seconds=user.used_duration_seconds,
                        daily_quota_seconds=quota_limit,
                        remaining_seconds=remaining,
                        requested_seconds=duration_seconds,
                    )
                )

        self._logger.info(
            f"Quota OK: user={user.id}, used={user.used_duration_seconds}s, "
            f"limit={quota_limit}, requested={duration_seconds}s"
        )

        return success((duration_seconds, user))

    async def _save_meeting_and_update_quota(
        self, meeting: Meeting, user: User, duration_seconds: float
    ) -> Result[None, Exception]:
        """Save meeting and update user quota in transaction."""
        save_result = await self._meeting_repository.save(meeting)
        if not save_result.success:
            await self._transaction_manager.rollback()
            return failure(save_result.error)

        user.increment_usage(duration_seconds)
        update_result = await self._user_repo.save(user)
        if not update_result.success:
            await self._transaction_manager.rollback()
            return failure(update_result.error)

        await self._transaction_manager.commit()
        return success(None)
