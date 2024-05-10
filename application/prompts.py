import threading
import time
from collections import deque
from copy import copy
from logging import getLogger
from pathlib import Path

from application.settings import settings


logger = getLogger(__name__)


class Prompts:
    def __init__(self) -> None:
        self._dataset: set[str] = set()
        """All known prompts."""
        self._latest: set[str] = set()
        """Fresh batch of prompts to share with validators."""
        self._submits: deque[set] = deque()
        """Recent submits, sorted by submit time."""
        self._last_backup_time = time.time()

        self.load(settings.resources)

    def load(self, path: Path) -> None:
        if not path.is_absolute():
            dataset_path = Path(__file__).parent.parent / path / "default_prompts.txt"
        else:
            dataset_path = Path(path) / "default_prompts.txt"

        if not dataset_path.exists():
            raise RuntimeError(f"Dataset file {dataset_path} not found")

        with dataset_path.open() as f:
            self._dataset = set(f.read().strip().split("\n"))

        logger.info(f"{len(self._dataset)} prompts loaded")

    def backup(self, path: Path) -> None:
        cur_time = int(time.time())
        file_name = f"prompts_{cur_time}.txt"
        dataset_path = path / file_name

        if not path.is_absolute():
            dataset_path = Path(__file__).resolve().parent.parent / dataset_path

        thread = threading.Thread(target=self._perform_backup, args=(dataset_path, copy(self._dataset)))
        thread.start()

    def _perform_backup(self, dataset_path: Path, data: set[str]) -> None:
        with dataset_path.open("w") as f:
            for prompt in data:
                f.write(prompt + "\n")

    def submit(self, batch: list[str]) -> None:
        """Add new prompts to the dataset."""

        unique = set(batch)
        prev_size = len(self._dataset)
        self._dataset.update(unique)

        logger.info(
            f"{len(batch)} prompts submitted. {len(unique)} unique prompts. "
            f"{len(self._dataset) - prev_size} new prompts"
        )

        self._submits.append(unique)
        self._latest.update(unique)

        logger.info(f"{len(self._latest)} freshly minted prompts")

        while len(self._submits) > 0 and len(self._latest) - len(self._submits[0]) > settings.sufficient_batch_size:
            oldest_submit = self._submits.popleft()
            self._latest = self._latest - oldest_submit

        logger.info(f"{len(self._latest)} prompts after prunning the old ones")

        if self._last_backup_time + settings.backup_interval > time.time():
            self._last_backup_time = time.time()
            self.backup(settings.resources)

    def get(self) -> list[str]:
        """Return the newest prompts."""
        latest_available = len(self._latest)
        if latest_available > settings.sufficient_batch_size:
            return list(self._latest)[: settings.sufficient_batch_size]

        return list(self._latest) + list(self._dataset)[: settings.sufficient_batch_size - latest_available]
