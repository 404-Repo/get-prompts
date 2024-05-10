import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.api_key = os.getenv("API_KEY", "default_api_key")
        """API-KEY to auth prompt generators."""
        self.resources = Path(os.getenv("PROMPTS_DIR", "resources"))
        """Folder with prompts. Used to load default_prompts and backup actual prompts."""
        self.backup_interval: int = int(os.getenv("BACKUP_INTERVAL", 60 * 60))  # One hour
        """Time interval to save new dataset to a file."""
        self.sufficient_batch_size: int = int(os.getenv("BATCH_SIZE", 100000))
        """Number of prompts to return to validators."""


settings = Settings()
