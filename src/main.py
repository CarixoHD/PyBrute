import asyncio
from pybrute.config import (
    SESSION_SIZE,
    SESSION_TIMEOUT,
    CONCURRENCY_LIMIT,
    NUM_WORKERS,
    BATCH_SIZE,
    MAX_REQUESTS_PER_SESSION,
    WORDLIST,
    MAX_RETRIES,
)
from pybrute.session_manager import SessionManager
from pybrute.utils import load_wordlist_to_queue, read_wordlist
from pybrute.counter import Counter
from pybrute.jobs.job import job
from pybrute.conc import ConcurrencyManager
from pybrute.bruteforcer import Bruteforcer


def initialize_session_manager():
    return SessionManager(
        size=SESSION_SIZE,
        max_requests_per_session=MAX_REQUESTS_PER_SESSION,
        timeout=SESSION_TIMEOUT,
    )


def initialize_concurrency_manager():
    return ConcurrencyManager(CONCURRENCY_LIMIT)


async def initialize_wordlist_queue():
    wordlist_queue = asyncio.Queue()
    wordlist = read_wordlist(WORDLIST)
    total_wordlist = await load_wordlist_to_queue(
        wordlist=wordlist, queue=wordlist_queue
    )
    return wordlist_queue, total_wordlist


async def run_bruteforce(session_manager, wordlist_queue, total_wordlist):
    stop_event = asyncio.Event()
    conc_manager = initialize_concurrency_manager()
    counter = Counter(conc_manager)

    print(f"[+] Wordlist loaded into queue: {total_wordlist}")
    await session_manager.init_sessions()
    print(f"[+] {SESSION_SIZE} sessions initialized.")

    brute = Bruteforcer(
        session_manager=session_manager,
        job=job,
        wordlist_queue=wordlist_queue,
        num_workers=NUM_WORKERS,
        stop_event=stop_event,
        conc_manager=conc_manager,
        total_wordlist=total_wordlist,
        batch_size=BATCH_SIZE,
        counter=counter,
        max_retries=MAX_RETRIES,
    )
    await brute.start()
    await brute.stop()
    print(f"[+] Total number of entries checked: {counter.counter}")


async def main():
    session_manager = initialize_session_manager()
    wordlist_queue, total_wordlist = await initialize_wordlist_queue()
    await run_bruteforce(session_manager, wordlist_queue, total_wordlist)


if __name__ == "__main__":
    asyncio.run(main())
