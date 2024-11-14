def read_wordlist(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


async def load_wordlist_to_queue(wordlist, queue):
    for word in wordlist:
        await queue.put(word)
    return len(wordlist)
