import aiohttp
from ..config import RESULTS, URL

async def fetch_report(session, dir):
    """
    Return True if only 1 match is enough
    Return None otherwise
    """
    if "." in dir:
        dir = dir.split(".")[0]
    url = f"{URL}/{dir}/get-reports"
    async with session.get(url, allow_redirects=False) as response:
        response_text = await response.text()
        if "was not found" not in response_text:
            RESULTS.append(dir)
    return None
