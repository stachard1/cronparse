"""Custom exceptions for cronparse."""


class CronParseError(ValueError):
    """Raised when a cron expression cannot be parsed or validated."""

    def __init__(self, expression: str, reason: str) -> None:
        self.expression = expression
        self.reason = reason
        super().__init__(f"Invalid cron expression '{expression}': {reason}")


class CronFieldError(CronParseError):
    """Raised when a specific field in a cron expression is invalid."""

    def __init__(self, expression: str, field: str, value: str, reason: str) -> None:
        self.field = field
        self.value = value
        super().__init__(expression, f"field '{field}' value '{value}' — {reason}")
