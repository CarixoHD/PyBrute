import aiohttp
import asyncio
from .config import SESSION_COOKIES
import tqdm

class ClientSessionWrapper(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request_count = 0

    async def _request(self, method, url, **kwargs):
        self._request_count += 1
        return await super()._request(method, url, **kwargs)

class SessionManager:
    def __init__(self, *, size, max_requests_per_session, timeout):
        self.size = size
        self.max_requests_per_session = max_requests_per_session
        self.timeout = timeout
        self.sessions = asyncio.Queue()

    async def init_sessions(self):
        with tqdm.tqdm(total=self.size, desc="Setting up sessions...") as pbar:
            tasks = [self.create_session() for _ in range(self.size)]
            sessions = await asyncio.gather(*tasks)
            for session in sessions:
                await self.sessions.put(session)
                pbar.update(1)

    async def close_sessions(self):
        while not self.sessions.empty():
            session = await self.sessions.get()
            await session.close()

    async def create_session(self):
        session = ClientSessionWrapper(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        if SESSION_COOKIES:
            session.cookie_jar.update_cookies(SESSION_COOKIES)
        return session

    async def get_session(self):
        return await self.sessions.get()

    async def release_session(self, session):
        if session._request_count >= self.max_requests_per_session:
            await session.close()
            session = await self.create_session()
        await self.sessions.put(session)
