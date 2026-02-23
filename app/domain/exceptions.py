class DomainError(Exception):
    """Base exception for all domain errors."""

    error_code: str = "DOMAIN_ERROR"
    status_code: int = 400


class DuplicateUsernameError(DomainError):
    """Raised when a username is already taken."""

    error_code = "DUPLICATE_USERNAME"
    status_code = 409


class DuplicateEmailError(DomainError):
    """Raised when an email is already registered."""

    error_code = "DUPLICATE_EMAIL"
    status_code = 409


class InvalidCredentialsError(DomainError):
    """Raised when login credentials are invalid."""

    error_code = "INVALID_CREDENTIALS"
    status_code = 401


class InactiveAccountError(DomainError):
    """Raised when an inactive user attempts to authenticate."""

    error_code = "INACTIVE_ACCOUNT"
    status_code = 403


class InvalidRefreshTokenError(DomainError):
    """Raised when a refresh token is invalid, expired, or revoked."""

    error_code = "INVALID_REFRESH_TOKEN"
    status_code = 401


class InvalidAccessTokenError(DomainError):
    """Raised when an access token is invalid or expired."""

    error_code = "INVALID_ACCESS_TOKEN"
    status_code = 401


class StorageError(DomainError):
    """Raised when an object storage operation fails."""

    error_code = "STORAGE_ERROR"
    status_code = 500


class StorageFileNotFoundError(DomainError):
    """Raised when a requested file does not exist in storage."""

    error_code = "FILE_NOT_FOUND"
    status_code = 404
