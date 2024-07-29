import asyncio
from .config import CONCURRENCY_LIMIT


class ConcurrencyManager:
    def __init__(self, init_lim=CONCURRENCY_LIMIT):
        self.init_lim = init_lim
        self.limit = init_lim
        self.semaphore = asyncio.Semaphore(init_lim)
        self.lock = asyncio.Lock()

    async def adjust(self, adjustment):
        async with self.lock:
            new_limit = max(self.init_lim, self.limit + adjustment)
            self.limit = new_limit
            self.semaphore = asyncio.Semaphore(new_limit)
