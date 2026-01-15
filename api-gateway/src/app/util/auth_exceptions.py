"""Authentication exceptions."""

UNAUTHORIZED_ERROR_MESSAGE = "Authentication failed"
TOKEN_VERIFICATION_INTERNAL_ERROR_MESSAGE = (
    "Internal error occurred during token verification"
)


class UnauthorizedError(Exception):
    """Authentication failed error."""

    def __init__(self, message: str = UNAUTHORIZED_ERROR_MESSAGE) -> None:
        super().__init__(message)
        self.message = UNAUTHORIZED_ERROR_MESSAGE

    @property
    def name(self) -> str:
        return "UnauthorizedError"


class InvalidTokenError(Exception):
    """Invalid token error."""

    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(message)
        self.message = UNAUTHORIZED_ERROR_MESSAGE

    @property
    def name(self) -> str:
        return "UnauthorizedError"


class TokenVerificationInternalError(Exception):
    """Token verification internal error."""

    def __init__(
        self, message: str = TOKEN_VERIFICATION_INTERNAL_ERROR_MESSAGE
    ) -> None:
        super().__init__(message)
        self.message = TOKEN_VERIFICATION_INTERNAL_ERROR_MESSAGE

    @property
    def name(self) -> str:
        return "TokenVerificationInternalError"
