"""Domain layer provider for DI container."""

from dishka import Provider, Scope, provide

from app.di_container.settings import settings
from app.domain.support.audio_analyzer.audio_analyzer import AudioAnalyzer
from app.domain.support.logger.logger import Logger
from app.infrastructure.logger.logger_impl import LoggerImpl


class DomainProvider(Provider):
    """Provider for domain layer services."""

    @provide(scope=Scope.REQUEST)
    def provide_audio_analyzer(self, logger: Logger) -> AudioAnalyzer:
        """Provide audio analyzer service."""
        return AudioAnalyzer(logger=logger)

    @provide(scope=Scope.APP)
    def provide_logger(self) -> Logger:
        """Provide logger singleton."""
        return LoggerImpl(name="app", level=settings.logging.level)
