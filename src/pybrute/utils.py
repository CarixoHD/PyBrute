# src/utils.py

from datetime import datetime, timezone


def gen_url():
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    url = f"https://google.com/?t={now_ms}"
    return url


def read_wordlist(file_path):
    with open(file_path, "r") as f:
        return list(filter(None, [i.strip() for i in f.readlines()]))


async def load_wordlist_to_queue(*, wordlist, queue):
    for i in wordlist:
        await queue.put(i)
    total = queue.qsize()
    return total
