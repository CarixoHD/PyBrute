import asyncio
from .session_manager import SessionManager
from .bruteforcer import Bruteforcer
from .counter import Counter
from .conc import ConcurrencyManager
from .utils import load_wordlist_to_queue, read_wordlist
from .config import (
    SESSION_TIMEOUT,
    MAX_REQUESTS_PER_SESSION,
    WORDLIST,
    NUM_WORKERS,
    BATCH_SIZE,
    MAX_RETRIES,
    CONCURRENCY_LIMIT,
    SESSION_SIZE,
)

class Runner:
    def __init__(self, user_func, *args, **kwargs):
        self.user_func = user_func
        self.args = args 
        self.kwargs = kwargs
        self.session_manager = SessionManager(max_requests_per_session=MAX_REQUESTS_PER_SESSION, timeout=SESSION_TIMEOUT, size=SESSION_SIZE)
        self.wordlist_queue = asyncio.Queue()
        self.stop_event = asyncio.Event()
        self.conc_manager = ConcurrencyManager(CONCURRENCY_LIMIT)
        self.counter = Counter(self.conc_manager)
        self.results = []

    async def setup(self):
        wordlist = read_wordlist(WORDLIST)
        total_wordlist = await load_wordlist_to_queue(
            wordlist=wordlist, queue=self.wordlist_queue
        )
        print(f"[+] Loaded {total_wordlist} entries from wordlist")
        await self.session_manager.init_sessions()
        print(f"[+] {SESSION_SIZE} sessions initialized")

    async def run(self):
        await self.setup()
        bruteforcer = Bruteforcer(
            session_manager=self.session_manager,
            job=self.job_wrapper,
            wordlist_queue=self.wordlist_queue,
            num_workers=NUM_WORKERS,
            stop_event=self.stop_event,
            batch_size=BATCH_SIZE,
            counter=self.counter,
            max_retries=MAX_RETRIES,
            conc_manager=self.conc_manager,
        )
        await bruteforcer.start()
        await bruteforcer.stop()
        print(f"[+] {self.counter.counter} attempts made")

    async def job_wrapper(self, session_manager, entry, stop_event, counter, retries):
        if stop_event.is_set():
            return False
        attempt = 0
        session = await session_manager.get_session()
        try:
            while attempt < retries:
                if stop_event.is_set():
                    return False
                try:
                    result = await self.user_func(session, entry, *self.args, **self.kwargs)
                    await counter.increment()
                    return result
                
                except Exception:
                    attempt += 1
                    if attempt >= retries:
                        return False
        finally:
            await session_manager.release_session(session)
