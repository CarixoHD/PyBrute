from .scripts.fetch_report import fetch_report

async def job(session_manager, dir, stop_event, counter, retries):
    if stop_event.is_set():
        return None

    attempt = 0
    session = await session_manager.get_session()

    while attempt < retries:
        try:
            result = await fetch_report(session, dir)
            await session_manager.release_session(session)
            await counter.increment()
            return result

        except Exception:
            attempt += 1
            if attempt == retries:
                await session_manager.release_session(session)
                return False
