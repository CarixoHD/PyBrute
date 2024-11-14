import asyncio


class Worker:
    def __init__(
        self,
        *,
        worker_id,
        session_manager,
        wordlist_queue,
        stop_event,
        job,
        batch_size,
        counter,
        max_retries,
        conc_manager,
    ):
        self.worker_id = worker_id
        self.session_manager = session_manager
        self.wordlist_queue = wordlist_queue
        self.stop_event = stop_event
        self.job = job
        self.batch_size = batch_size
        self.counter = counter
        self.max_retries = max_retries
        self.conc_manager = conc_manager
        self.current_tasks = []

    async def run(self):
        while not self.stop_event.is_set():
            entries = []
            for _ in range(self.batch_size):
                if self.stop_event.is_set():
                    break
                try:
                    entry = self.wordlist_queue.get_nowait()
                    entries.append(entry)
                except asyncio.QueueEmpty:
                    break
            if not entries:
                break

            tasks = [asyncio.create_task(self.execute_job(entry)) for entry in entries]
            self.current_tasks.extend(tasks)

            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                break

            for task in tasks:
                self.current_tasks.remove(task)

    async def cancel_tasks(self):
        current_task = asyncio.current_task()
        tasks_to_cancel = [t for t in self.current_tasks if t != current_task]
        for task in tasks_to_cancel:
            task.cancel()
        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

    async def execute_job(self, password):
        async with self.conc_manager.semaphore:
            if self.stop_event.is_set():
                return
            try:
                result = await self.job(
                    self.session_manager,
                    password,
                    self.stop_event,
                    self.counter,
                    self.max_retries,
                )
                if result:
                    self.stop_event.set()
                    await self.cancel_tasks()
                elif result is False:
                    await self.counter.increment_fails()
                elif result is None:
                    await self.counter.increment_success()
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
