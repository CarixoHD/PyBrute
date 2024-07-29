import asyncio
from tqdm.asyncio import tqdm
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
        conc_manager,
        total_wordlist,
        batch_size,
        counter,
        max_retries,
    ):
        self.session_manager = session_manager
        self.job = job
        self.wordlist_queue = wordlist_queue
        self.stop_event = stop_event
        self.conc_manager = conc_manager
        self.total_wordlist = total_wordlist
        self.progress_counter = tqdm(total=total_wordlist, desc="Progress", position=0)
        self.batch_size = batch_size
        self.counter = counter
        self.max_retries = max_retries
        self.workers = [
            Worker(
                worker_id=worker_id,
                session_manager=self.session_manager,
                wordlist_queue=wordlist_queue,
                stop_event=stop_event,
                job=job,
                conc_manager=conc_manager,
                progress_counter=self.progress_counter,
                batch_size=batch_size,
                counter=counter,
                max_retries=max_retries,
            )
            for worker_id in range(num_workers)
        ]

    async def start(self):
        tasks = [asyncio.create_task(worker.run()) for worker in self.workers]
        await asyncio.gather(*tasks)
        self.progress_counter.close()

    async def stop(self):
        await self.session_manager.close_sessions()
