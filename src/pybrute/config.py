import yaml


class Config:
    def __init__(self, config_file="../config/config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, "r") as file:
            return yaml.safe_load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default


config = Config()

SESSION_SIZE = config.get("session.size")
SESSION_TIMEOUT = config.get("session.timeout")
CONCURRENCY_LIMIT = config.get("session.concurrency_limit")

NUM_WORKERS = config.get("workers.num_workers")
BATCH_SIZE = config.get("workers.batch_size")

MAX_RETRIES = config.get("retry.max_retries")
MAX_REQUESTS_PER_SESSION = config.get("retry.max_requests_per_session")

WORDLIST = config.get("paths.wordlist")

SESSION_COOKIES = config.get("session_init.session_cookies")
SESSION_HEADER = config.get("session_init.session_headers")
SESSION_DATA = config.get("session_init.session_data")

URL = config.get("session_init.url")
