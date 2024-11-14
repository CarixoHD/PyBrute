import asyncio
from .worker import Worker

class Bruteforcer:
    def __init__(
        self,
        *,
        session_manager,
        job,
        wordlist_queue,
        num_workers,
        stop_event,
        batch_size,
        counter,
        max_retries,
        conc_manager,
    ):
        self.session_manager = session_manager
        self.job = job
        self.wordlist_queue = wordlist_queue
        self.stop_event = stop_event
        self.batch_size = batch_size
        self.counter = counter
        self.max_retries = max_retries
        self.conc_manager = conc_manager
        self.workers = [
            Worker(
                worker_id=worker_id,
                session_manager=self.session_manager,
                wordlist_queue=self.wordlist_queue,
                stop_event=self.stop_event,
                job=self.job,
                batch_size=self.batch_size,
                counter=self.counter,
                max_retries=self.max_retries,
                conc_manager=self.conc_manager,
            )
            for worker_id in range(num_workers)
        ]
        self.worker_tasks = []

    async def start(self):
        self.worker_tasks = [asyncio.create_task(worker.run()) for worker in self.workers]
        try:
            await asyncio.gather(*self.worker_tasks)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        for task in self.worker_tasks:
            task.cancel()
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        await self.session_manager.close_sessions()
