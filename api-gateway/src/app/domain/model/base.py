"""Base entity class."""

from typing import Any, Self, TypeVar, cast

IdType = TypeVar("IdType")


class Entity:
    """
    Base class for domain entities.
    Entities are defined by unique identity (id).
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is Entity:
            raise TypeError("Base Entity cannot be instantiated directly.")
        return object.__new__(cls)

    def __init__(self, *, id: IdType) -> None:
        self.id = id

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modifying id after set"""
        if name == "id" and getattr(self, "id", None) is not None:
            raise AttributeError("Changing entity ID is not permitted.")
        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        """Two entities are equal if they have same id"""
        return type(self) is type(other) and cast(Self, other).id == self.id

    def __hash__(self) -> int:
        """Hash based on type and id"""
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r})"
