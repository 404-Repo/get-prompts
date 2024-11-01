import copy
import random
import threading
import time
from collections import deque, defaultdict
from pathlib import Path
import glob

import bittensor as bt
from application.db import PromptsDB


class Prompts:
    def __init__(self, config: bt.config) -> None:
        self.config = copy.deepcopy(config)

        self._dataset: set[str] = set()
        """All known prompts."""
        self._latest: set[str] = set()
        """Fresh batch of prompts to share with validators."""
        self._submits: deque[set] = deque()
        """Recent submits, sorted by submit time."""
        self._last_backup_time = time.time()
        
        # Buffer for collecting prompts before DB upload
        self._prompt_buffer: dict[str, list[str]] = defaultdict(list)
        """Buffer to collect prompts before uploading to DB"""
        
        # Initialize DB handler
        self._db = PromptsDB(config)

        self.load(Path(config.resources))

    def upload_backups_to_db(self) -> None:
        """Read all backup files and upload prompts to the database."""
        try:
            # Get all backup files
            backup_path = Path(self.config.resources)
            if not backup_path.is_absolute():
                backup_path = Path(__file__).parent.parent / backup_path
            
            backup_files = glob.glob(str(backup_path / "prompts_*.txt"))
            self._db.upload_from_files(backup_files)
            
        except Exception as e:
            bt.logging.error(f"Failed to upload backups to database: {str(e)}")
            raise

    def _upload_buffer_to_db(self, client_id) -> None:
        """Upload buffered prompts to the database."""
        if not self._prompt_buffer:
            return
            
        try:
            self._db.upload_prompts(self._prompt_buffer[client_id], client_id)
            self._prompt_buffer[client_id].clear()
        except Exception as e:
            bt.logging.error(f"Failed to upload prompts to database: {str(e)}")
            raise

    def load(self, path: Path) -> None:
        if not path.is_absolute():
            dataset_path = Path(__file__).parent.parent / path / "default_prompts.txt"
        else:
            dataset_path = Path(path) / "default_prompts.txt"

        if not dataset_path.exists():
            raise RuntimeError(f"Dataset file {dataset_path} not found")

        with dataset_path.open() as f:
            self._dataset = set(f.read().strip().split("\n"))

        bt.logging.info(f"{len(self._dataset)} prompts loaded")

    def backup(self, path: Path) -> None:
        cur_time = int(time.time())
        file_name = f"prompts_{cur_time}.txt"
        dataset_path = path / file_name

        if not path.is_absolute():
            dataset_path = Path(__file__).resolve().parent.parent / dataset_path

        thread = threading.Thread(target=self._perform_backup, args=(dataset_path, copy.copy(self._dataset)))
        thread.start()

    def _perform_backup(self, dataset_path: Path, data: set[str]) -> None:
        with dataset_path.open("w") as f:
            for prompt in data:
                f.write(prompt + "\n")

    def submit(self, batch: list[str], client_id: str) -> None:
        """Add new prompts to the dataset and buffer them for DB upload."""
        unique = set(batch)
        prev_size = len(self._dataset)
        self._dataset.update(unique)

        bt.logging.info(
            f"{len(batch)} prompts submitted. {len(unique)} unique prompts. "
            f"{len(self._dataset) - prev_size} new prompts"
        )

        self._submits.append(unique)
        self._latest.update(unique)
        
        self._prompt_buffer[client_id].extend(unique)
        
        if len(self._prompt_buffer[client_id]) >= 3000:
            self._upload_buffer_to_db(client_id)

        bt.logging.info(f"{len(self._latest)} freshly minted prompts")

        while len(self._submits) > 0 and len(self._latest) - len(self._submits[0]) > self.config.sufficient_batch_size:
            oldest_submit = self._submits.popleft()
            self._latest = self._latest - oldest_submit

        bt.logging.info(f"{len(self._latest)} prompts after prunning the old ones")

        if self._last_backup_time + self.config.backup_interval < time.time():
            self._last_backup_time = time.time()
            self.backup(Path(self.config.resources))

    def get(self) -> list[str]:
        """Return the newest prompts."""
        latest_available = len(self._latest)
        if latest_available > self.config.sufficient_batch_size:
            return list(self._latest)[: self.config.sufficient_batch_size]

        r = list(self._dataset)
        random.shuffle(r)
        return list(self._latest) + r[: self.config.sufficient_batch_size - latest_available]
