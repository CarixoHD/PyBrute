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
        conc_manager,
        progress_counter,
        batch_size,
        counter,
        max_retries,
    ):
        self.worker_id = worker_id
        self.session_manager = session_manager
        self.wordlist_queue = wordlist_queue
        self.stop_event = stop_event
        self.job = job
        self.conc_manager = conc_manager
        self.progress_counter = progress_counter
        self.batch_size = batch_size
        self.counter = counter
        self.max_retries = max_retries

    async def run(self):
        while not (self.stop_event.is_set()) or not self.wordlist_queue.empty():
            passwords = []
            for _ in range(self.batch_size):
                if self.wordlist_queue.empty():
                    break
                password = await self.wordlist_queue.get()
                passwords.append(password)
            if len(passwords) == 0:
                break

            tasks = [self.execute_job(password) for password in passwords]
            await asyncio.gather(*tasks)

    async def execute_job(self, password):
        async with self.conc_manager.semaphore:
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
                elif result is False:
                    self.wordlist_queue.put_nowait(password)
                    await self.counter.increment_fails()

                elif result is None:
                    self.progress_counter.update(1)
                    await self.counter.increment_success()

            except Exception as e:
                print(f"Error processing password {password}: {str(e)}")
