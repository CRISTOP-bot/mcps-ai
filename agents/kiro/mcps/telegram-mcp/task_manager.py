"""Task manager for async processing of Telegram messages."""

import asyncio
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger("task_manager")


class TaskManager:
    """Manages async task processing with per-chat queues."""

    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self._queues = defaultdict(deque)  # chat_id -> deque of tasks
        self._active = {}  # task_id -> task info
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._processing = defaultdict(bool)  # chat_id -> bool
        self._counter = 0

    async def enqueue(self, chat_id, coro_func, *args, **kwargs):
        """Enqueue a task for processing."""
        self._counter += 1
        task_id = self._counter
        task = {
            "id": task_id,
            "chat_id": chat_id,
            "coro_func": coro_func,
            "args": args,
            "kwargs": kwargs,
            "status": "pending",
            "created_at": time.time(),
            "result": None,
            "error": None,
        }
        async with self._lock:
            self._queues[chat_id].append(task)
        logger.info(f"Task {task_id} enqueued for chat {chat_id}")
        return task_id

    async def process_queue(self, chat_id):
        """Process all pending tasks for a chat in order."""
        while True:
            async with self._lock:
                if not self._queues[chat_id]:
                    self._processing[chat_id] = False
                    break
                task = self._queues[chat_id].popleft()
                self._processing[chat_id] = True

            task["status"] = "running"
            self._active[task["id"]] = task

            async with self._semaphore:
                try:
                    task["result"] = await task["coro_func"](*task["args"], **task["kwargs"])
                    task["status"] = "completed"
                except Exception as e:
                    task["error"] = str(e)
                    task["status"] = "failed"
                    logger.error(f"Task {task['id']} failed: {e}")
                finally:
                    task["completed_at"] = time.time()
                    del self._active[task["id"]]

    def is_processing(self, chat_id):
        return self._processing.get(chat_id, False)

    def get_active_tasks(self):
        return list(self._active.values())

    def get_queue_size(self, chat_id):
        return len(self._queues.get(chat_id, []))

    async def cancel_chat(self, chat_id):
        """Cancel all pending tasks for a chat."""
        async with self._lock:
            count = len(self._queues[chat_id])
            self._queues[chat_id].clear()
            return count
