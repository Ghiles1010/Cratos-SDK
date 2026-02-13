"""
Cratos SDK - Simple HTTP-based task scheduling client with WebSocket support.
"""

from .client import CratosClient
from .models.task import Task
from .models.websocket_message import WebSocketMessage
from .task.task_manager import TaskManager
from .models.enums import WebSocketMessageType, ExecutionStatus

__all__ = [
    'CratosClient',
    'Task',
    'TaskManager',
    'WebSocketMessage',
    'WebSocketMessageType',
    'ExecutionStatus'
]
__version__ = '0.6.0' 