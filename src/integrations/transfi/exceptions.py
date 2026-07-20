class TransfiError(Exception):
    """Base class for all Transfi integration errors."""


class TransfiRequestError(TransfiError):
    """Transfi's API returned a non-success response, or the request itself failed
    (network error, timeout)."""
