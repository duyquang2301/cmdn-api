"""Authentication provider for DI container."""

from dishka import Provider, Scope, provide

from app.di_container.settings import settings
from app.infrastructure.auth.jwt_validator import JWTValidator


class AuthProvider(Provider):
    """Provider for authentication services."""

    @provide(scope=Scope.APP)
    def provide_jwt_validator(self) -> JWTValidator:
        """Provide JWT validator singleton.

        Returns:
            JWTValidator: Configured JWT validator instance
        """
        return JWTValidator(
            audience=settings.auth0.audience,
            issuer_base_url=settings.auth0.issuer_base_url,
        )
