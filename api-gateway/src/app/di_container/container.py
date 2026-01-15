"""DI container configuration.

Provides dependency injection setup using Dishka.
Providers are organized by architectural layer.
"""

from collections.abc import Iterable

from dishka import AsyncContainer, Provider, make_async_container

from app.di_container.providers import (
    AuthProvider,
    DomainProvider,
    InfrastructureProvider,
    UseCaseProvider,
)


def get_providers() -> Iterable[Provider]:
    """Get all DI providers organized by layer.

    Returns:
        Collection of providers (Auth, Domain, Infrastructure, UseCase)
    """
    return (
        AuthProvider(),
        DomainProvider(),
        InfrastructureProvider(),
        UseCaseProvider(),
    )


def create_container(*additional_providers: Provider) -> AsyncContainer:
    """Create DI container with all providers.

    Args:
        *additional_providers: Optional providers for testing

    Returns:
        Configured async container
    """
    return make_async_container(
        *get_providers(),
        *additional_providers,
    )
