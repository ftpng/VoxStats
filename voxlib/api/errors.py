class APIError(Exception):
    """
    Base exception for all Voxyl API-related errors.

    Args:
        message (str): A descriptive error message.
    """
    def __init__(self, message: str):
        super().__init__(message)


class RateLimitError(APIError):
    """
    Exception raised when the Voxyl API rate limit is exceeded.

    Args:
        message (str, optional): Custom error message.
            Defaults to "Rate limit exceeded".
    """
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message)


class BadRequestError(APIError):
    """
    Exception raised when the Voxyl API returns a bad request error
    (e.g., invalid arguments or missing parameters).

    Args:
        message (str, optional): Custom error message.
            Defaults to "Bad request".
    """
    def __init__(self, message="Bad request"):
        super().__init__(message)


class UnexpectedStatusError(APIError):
    """
    Exception raised when the Voxyl API returns an unexpected HTTP status code.

    Args:
        message (str): A descriptive error message, typically including
            the unexpected status code or response content.
    """
    def __init__(self, message):
        super().__init__(message)