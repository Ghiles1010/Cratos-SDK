# Cratos SDK

<div align="center">

**Simple Python SDK for the Cratos task scheduler**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)

</div>

---

## Installation

```bash
git clone https://github.com/Ghiles1010/Cratos-SDK.git
cd Cratos-SDK
pip install -e .
```

## Quick Start

```python
import asyncio
from cratos import CratosClient, Task
from datetime import datetime, timedelta

client = CratosClient(api_key="your_api_key")

async def main():
    # Schedule a one-off task (batch API - always pass a list)
    task = Task(
        task_name="send_email",
        callback_url="https://your-app.com/webhook",
        task_kwargs={"to": "user@example.com"},
        schedule_time=datetime.now() + timedelta(seconds=10)
    )
    task_ids = await client.tasks.schedule([task])
    task_id = task_ids[0]
    
    # List all tasks (synchronous)
    all_tasks = client.tasks.list()
    
    # Get task (batch API)
    tasks = await client.tasks.get([task_id])
    
    # Cancel task (batch API)
    await client.tasks.cancel([task_id])

asyncio.run(main())
```

## Task Types

```python
# One-off task
Task(
    task_name="send_email",
    callback_url="https://your-app.com/webhook",
    schedule_time=datetime.now() + timedelta(seconds=10)
)

# Cron task
Task(
    task_name="daily_report",
    callback_url="https://your-app.com/webhook",
    schedule_type="cron",
    cron_expression="0 9 * * *",
    task_timezone="America/New_York"
)

# Interval task
Task(
    task_name="health_check",
    callback_url="https://your-app.com/webhook",
    schedule_type="interval",
    interval_seconds=300
)
```

## API Methods

**All task operations are batch-only** - methods accept lists and return lists.

### Synchronous
- `list()` - List all tasks
- `list_scheduled()` - List scheduled tasks

### Async (batch)
- `schedule(tasks: List[Task]) -> List[str]` - Schedule tasks
- `get(task_ids: List[str]) -> List[Optional[Task]]` - Get tasks
- `update(tasks: List[Task]) -> List[Task]` - Update tasks
- `cancel(task_ids: List[str]) -> List[Task]` - Cancel tasks
- `pause(task_ids: List[str]) -> List[Task]` - Pause tasks
- `resume(task_ids: List[str]) -> List[Task]` - Resume tasks
- `retry(task_ids: List[str]) -> List[Task]` - Retry tasks
- `delete(task_ids: List[str]) -> List[bool]` - Delete tasks
- `get_execution_history(task_ids: List[str]) -> List[...]` - Get execution history

### WebSocket
- `subscribe_to_task(task_id, on_result, ...)` - Subscribe to real-time updates
- `unsubscribe_from_task(task_id)` - Unsubscribe
- `close()` - Close connections

## WebSocket Example

```python
def handle_result(message):
    if message.type == WebSocketMessageType.EXECUTION_RESULT:
        print(f"Task {message.task_id} completed: {message.status}")

client.subscribe_to_task(task_id, on_result=handle_result)
```

## Batch Operations

```python
# Schedule multiple tasks
tasks = [Task(task_name=f"task_{i}", callback_url="...") for i in range(10)]
task_ids = await client.tasks.schedule(tasks)

# Cancel all at once
await client.tasks.cancel(task_ids)
```

## Related Projects

- **[Cratos](https://github.com/Ghiles1010/Cratos)** - Backend service
- **[Cratos UI](https://github.com/Ghiles1010/Cratos-UI)** - Web interface

## License

MIT License - see [LICENSE](LICENSE) file for details.
