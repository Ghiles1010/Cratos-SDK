"""WebSocket methods for CratosClient."""

import logging
import threading
import time
import websocket
import json
from typing import Callable, Dict, Optional, TYPE_CHECKING
from ..models.websocket_message import WebSocketMessage
from ..models.enums import WebSocketMessageType

if TYPE_CHECKING:
    from websocket import WebSocketApp

logger = logging.getLogger(__name__)


class WebSocketOperations:
    """WebSocket operations for CratosClient."""
    
    def subscribe_to_task(
        self,
        task_id: str,
        on_result: Callable[[WebSocketMessage], None],
        on_error: Optional[Callable[[Exception], None]] = None,
        on_connect: Optional[Callable[[], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None,
        ping_interval: int = 30
    ) -> str:
        """
        Subscribe to real-time execution results for a task via WebSocket.
        
        Args:
            task_id: Task ID to subscribe to
            on_result: Callback function called when execution result is received
            on_error: Optional callback for connection errors
            on_connect: Optional callback when connection is established
            on_disconnect: Optional callback when connection is closed
            ping_interval: Interval in seconds to send ping messages (default: 30)
        
        Returns:
            Subscription ID (same as task_id for single task subscriptions)
        
        Example:
            ```python
            def handle_result(message: WebSocketMessage):
                if message.type == WebSocketMessageType.EXECUTION_RESULT:
                    print(f"Task {message.task_id} completed: {message.status}")
            
            client.subscribe_to_task("task-123", on_result=handle_result)
            ```
        """
        topic = f"task:{task_id}"
        ws_url = f"{self.websocket_base_url}/ws/subscribe/{topic}"
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                ws_message = WebSocketMessage(**data)
                
                if ws_message.type == WebSocketMessageType.SUBSCRIBED:
                    logger.info(f"Subscribed to topic: {topic}")
                    if on_connect:
                        on_connect()
                elif ws_message.type == WebSocketMessageType.EXECUTION_RESULT:
                    logger.info(f"Received execution result for task {task_id}")
                    on_result(ws_message)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse WebSocket message: {e}")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                if on_error:
                    on_error(e)
        
        def on_error_handler(ws, error):
            logger.error(f"WebSocket error for {topic}: {error}")
            if on_error:
                on_error(error)
        
        def on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket closed for {topic}")
            if topic in self._active_websockets:
                del self._active_websockets[topic]
            if topic in self._websocket_threads:
                del self._websocket_threads[topic]
            if on_disconnect:
                on_disconnect()
        
        def on_open(ws):
            logger.info(f"WebSocket connection opened for {topic}")
        
        def run_websocket():
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error_handler,
                on_close=on_close,
                on_open=on_open
            )
            self._active_websockets[topic] = ws
            
            # Start ping thread
            def ping_loop():
                while topic in self._active_websockets:
                    time.sleep(ping_interval)
                    if topic in self._active_websockets:
                        try:
                            ws.send("ping")
                        except Exception as e:
                            logger.warning(f"Failed to send ping: {e}")
                            break
            
            ping_thread = threading.Thread(target=ping_loop, daemon=True)
            ping_thread.start()
            
            # Run forever (until disconnected)
            ws.run_forever()
        
        # Start WebSocket in a separate thread
        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()
        self._websocket_threads[topic] = thread
        
        return topic
    
    def unsubscribe_from_task(self, task_id: str) -> bool:
        """
        Unsubscribe from task execution results.
        
        Args:
            task_id: Task ID to unsubscribe from
        
        Returns:
            True if successfully unsubscribed, False if not subscribed
        """
        topic = f"task:{task_id}"
        if topic in self._active_websockets:
            try:
                ws = self._active_websockets[topic]
                ws.send("unsubscribe")
                ws.close()
                return True
            except Exception as e:
                logger.error(f"Error unsubscribing from {topic}: {e}")
                return False
        return False

