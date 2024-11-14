import asyncio


class Counter:
    def __init__(self, conc_manager):
        self.fails = 0
        self.success = 0
        self.counter = 0
        self.conc_manager = conc_manager
        self.lock = asyncio.Lock()

    async def increment(self):
        async with self.lock:
            self.counter += 1

    async def increment_fails(self):
        async with self.lock:
            self.fails += 1
            await self.evaluate()

    async def increment_success(self):
        async with self.lock:
            self.success += 1
            await self.evaluate()

    async def evaluate(self):
        total = self.success + self.fails
        if total > 1:
            success_rate = (self.success / total) * 100
            if success_rate > 60:
                await self.conc_manager.adjust(10)
            elif success_rate < 60:
                await self.conc_manager.adjust(-10)
            self.reset()

    def reset(self):
        self.success = 0
        self.fails = 0
