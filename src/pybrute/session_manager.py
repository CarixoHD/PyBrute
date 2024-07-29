import aiohttp
import asyncio
from .config import SESSION_COOKIES, SESSION_DATA, SESSION_HEADER, URL
import tqdm


class ClientSessionWrapper(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request_count = 0

    def post(self, url, *, data=None, **kwargs):
        self._request_count += 1
        return super().post(url, data=data, **kwargs)

    def get(self, url, *, data=None, **kwargs):
        self._request_count += 1
        return super().get(url, data=data, **kwargs)


class SessionManager:
    def __init__(self, *, size, max_requests_per_session, timeout):
        self.size = size
        self.max_requests_per_session = max_requests_per_session
        self.timeout = timeout
        self.sessions = asyncio.Queue()
        self.lock = asyncio.Lock()

    async def init_sessions(self):
        async with self.lock:
            with tqdm.tqdm(total=self.size, desc="Setting up sessions...") as pbar:
                sessions = await asyncio.gather(
                    *[self.create_session() for _ in range(self.size)]
                )
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
        try:
            async with session.get(
                url=URL,
                headers=SESSION_HEADER,
                data=SESSION_DATA,
                allow_redirects=False,
            ):
                pass
            session.cookie_jar.update_cookies(SESSION_COOKIES)
            return session
        except (asyncio.TimeoutError, aiohttp.ClientError):
            await session.close()
            return await self.create_session()

    async def get_session(self):
        async with self.lock:
            while self.sessions.empty():
                await asyncio.sleep(0.1)
            session = await self.sessions.get()
            return session

    async def release_session(self, session):
        if session._request_count >= self.max_requests_per_session:
            await session.close()
            session = await self.create_session()
        self.sessions.put_nowait(session)
