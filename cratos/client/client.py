"""CratosClient - Main client class for the Cratos SDK."""

import logging
import threading
import requests
import websocket
from typing import Dict, Optional
from urllib.parse import urlparse
from .client_websocket import WebSocketOperations
from ..task.task_manager import TaskManager

logger = logging.getLogger(__name__)

# Default API endpoint
DEFAULT_API_URL = "http://localhost:8001"


class CratosClient(WebSocketOperations):
    """
    Main client for the Cratos server.
    
    Provides task scheduling functionality via REST API and WebSocket support.
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = DEFAULT_API_URL, 
        timeout: int = 30,
        websocket_base_url: Optional[str] = None
    ):
        """
        Initialize the Cratos client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the Cratos API (defaults to http://localhost:8001)
            timeout: Request timeout in seconds
            websocket_base_url: Base URL for WebSocket gateway (defaults to ws://localhost:8000 or derived from base_url)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Api-Key {api_key}',
            'Content-Type': 'application/json'
        })
        
        # Determine WebSocket base URL
        if websocket_base_url:
            self.websocket_base_url = websocket_base_url.rstrip('/')
        else:
            # Derive from base_url or use default
            parsed = urlparse(base_url)
            if parsed.scheme in ('http', 'https'):
                ws_scheme = 'wss' if parsed.scheme == 'https' else 'ws'
                # Default to localhost:8000 for local dev, otherwise use same host
                if 'localhost' in parsed.netloc or '127.0.0.1' in parsed.netloc:
                    self.websocket_base_url = 'ws://localhost:8000'
                else:
                    # Use same host but default to port 8000
                    netloc = parsed.netloc.split(':')[0]  # Remove port if present
                    self.websocket_base_url = f'{ws_scheme}://{netloc}:8000'
            else:
                self.websocket_base_url = 'ws://localhost:8000'
        
        self._active_websockets: Dict[str, websocket.WebSocketApp] = {}
        self._websocket_threads: Dict[str, threading.Thread] = {}
        
        # Initialize task manager
        self.tasks = TaskManager(self)

    def close(self):
        """Close the session and all WebSocket connections."""
        # Close all WebSocket connections
        for topic in list(self._active_websockets.keys()):
            self.unsubscribe_from_task(topic.split(':')[1] if ':' in topic else topic)
        
        # Close HTTP session
        self.session.close()
