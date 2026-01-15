from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    """
    Base for immutable value objects.
    Fields with repr=False are hidden. Use ClassVar[Final[T]] for class constants.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("Base ValueObject cannot be instantiated directly.")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field!")
        return object.__new__(cls)

    def __post_init__(self) -> None:
        """Hook for validation and invariants."""

    def __repr__(self) -> str:
        """String representation. Hidden fields show '<hidden>'."""
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        """Build repr value. Single field shows value, multiple show name=value."""
        items = [f for f in fields(self) if f.repr]
        if not items:
            return "<hidden>"
        if len(items) == 1:
            return f"{getattr(self, items[0].name)!r}"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
