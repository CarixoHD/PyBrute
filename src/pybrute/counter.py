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
            await self.evaluate()
            self.fails += 1

    async def increment_success(self):
        async with self.lock:
            await self.evaluate()
            self.success += 1

    async def evaluate(self):
        total = self.success + self.fails
        if total > 1:
            success_rate = round((self.success / total) * 100)
            # print("SUCCESS RATE: ", success_rate)
            # print("FAILS: ", self.fails)
            # print("SUCCESS: ", self.success)
            if success_rate > 60:
                await self.conc_manager.adjust(100)
            elif success_rate < 60:
                await self.conc_manager.adjust(-100)
            # self.reset()

    def reset(self):
        self.success = 0
        self.fails = 0
