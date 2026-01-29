class AlertingSystemError(Exception):
    """Base exception for all alerting system errors."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(AlertingSystemError):
    """Raised when a requested entity is not found."""

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id '{entity_id}' not found")


class DatabaseError(AlertingSystemError):
    """Raised when a database operation fails."""

    pass


class MessageQueueError(AlertingSystemError):
    """Raised when message queue operations fail."""

    pass


class CacheError(AlertingSystemError):
    """Raised when cache operations fail."""

    pass


class ValidationError(AlertingSystemError):
    """Raised when validation fails."""

    pass
