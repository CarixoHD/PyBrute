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
    git clone https://github.com/your-username/pybrute.git
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

Create your custom bruteforce script in the `scripts/` folder. For example, `fetch_report.py`:

```python
import aiohttp
from ..config import RESULTS, URL

async def fetch_report(session, dir):
    if "." in dir:
        dir = dir.split(".")[0]
    url = f"{URL}/{dir}/get-reports"
    async with session.get(url, allow_redirects=False) as response:
        response_text = await response.text()
        if "was not found" not in response_text:
            RESULTS.append(dir)
    return None
```
**Note:** If you want the bruteforce to stop after one match, return `True`. If you want to find all the matches, return `None`.

### Integrating the Custom Script

Edit `job.py` to import and use your custom function:

```python
# import the function
from .scripts.fetch_report import fetch_report

async def job(session_manager, dir, stop_event, counter, retries):
    if stop_event.is_set():
        return None

    attempt = 0
    session = await session_manager.get_session()

    while attempt < retries:
        try:
            # run the function
            result = await fetch_report(session, dir)
            await session_manager.release_session(session)
            await counter.increment()
            return result

        except Exception:
            attempt += 1
            if attempt == retries:
                await session_manager.release_session(session)
                return False
```

### Configuring the Bruteforcer

Adjust the settings in `config.yaml`. This is also where you specify the wordlist you want to use, the url, the session and worker parameters, as well as headers, cookies, and payloads being used in the initial session setup.

