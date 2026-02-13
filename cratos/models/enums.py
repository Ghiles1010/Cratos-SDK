"""Enums for the Cratos SDK."""

from enum import Enum


class ExecutionStatus(str, Enum):
    """Valid execution status values."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WebSocketMessageType(str, Enum):
    """Valid WebSocket message types."""
    SUBSCRIBED = "subscribed"
    EXECUTION_RESULT = "execution_result"

