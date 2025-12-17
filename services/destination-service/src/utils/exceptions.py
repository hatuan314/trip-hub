class DestinationServiceError(Exception):
    """Base exception for destination service."""


class NotFoundError(DestinationServiceError):
    pass
