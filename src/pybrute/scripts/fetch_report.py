import aiohttp

async def fetch_report(session, dir):
    """
    Return True if only 1 match is enough
    Return None otherwise
    """
    if "." in dir:
        dir = dir.split(".")[0]
    url = f"https://google.com/{dir}/get-reports"
    async with session.get(url, allow_redirects=False) as response:
        response_text = await response.text()
        if "was not found" not in response_text:
            print("FOUND")
    return None
