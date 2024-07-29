import aiohttp


async def job(session_manager, dir, stop_event, counter, retries):
    if stop_event.is_set():
        return None
    if "." in dir:
        dir = dir.split(".")[0]
    url = f"https://google.com/{dir}"
    attempt = 0
    session = await session_manager.get_session()
    while True:
        try:
            async with session.post(
                url,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                response_text = await response.text()
                await counter.increment()
                if "found on this" not in response_text:
                    print(f"[+] {url} - {response.status}")
            await session_manager.release_session(session)
            return None

        except Exception:
            attempt += 1
            if attempt == retries:
                await session_manager.release_session(session)
                return False
