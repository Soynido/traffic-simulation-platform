"""
Async Redis queue client for simulation jobs.
Compatible with workers' expected queues.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict

import redis.asyncio as redis


PENDING_QUEUE = "simulation:pending"


class RedisQueueClient:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: redis.Redis | None = None

    async def _conn(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
        return self._client

    async def enqueue_task(self, payload: Dict[str, Any]) -> str:
        """Enqueue a simulation job for workers to process.

        Ensures an `id` field exists and pushes JSON to the pending queue.
        """
        if "id" not in payload:
            payload["id"] = str(uuid.uuid4())
        client = await self._conn()
        await client.lpush(PENDING_QUEUE, json.dumps(payload))
        return payload["id"]

