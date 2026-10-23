"""Application-specific exceptions."""


class AppError(Exception):
    """Base class for expected, user-facing errors."""


class ValidationError(AppError):
    """Input failed validation."""


class NotFoundError(AppError):
    """Requested record does not exist."""


class DuplicateError(AppError):
    """Record already exists."""


class InUseError(AppError):
    """Record is referenced by other data and cannot be deleted."""