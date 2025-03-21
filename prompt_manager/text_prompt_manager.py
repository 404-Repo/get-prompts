import copy
import random
import threading
import time
from collections import deque
from pathlib import Path

import bittensor as bt
from main.config import config

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import TextPromptBatch


class TextPromptManager(BasePromptManager[TextPromptBatch]):
    _DEFAULT_PROMPTS_FILENAME: str = "default_prompts.txt"

    def __init__(self, *, resources_dir: Path, batch_size: int, backup_interval: int) -> None:
        super().__init__(resources_dir=resources_dir, batch_size=batch_size)
        self._dataset: set[str] = set()
        """All known prompts."""
        self._latest: set[str] = set()
        """Fresh batch of prompts to share with validators."""
        self._submits: deque[set[str]] = deque()
        """Recent submits, sorted by submit time."""
        self._last_backup_time: float = time.time()
        self._backup_interval: int = backup_interval
        self._load_default_prompts(self._resource_dir / self._DEFAULT_PROMPTS_FILENAME)

    def submit(self, *, batch: TextPromptBatch) -> None:  # type: ignore
        """Add new prompts to the dataset."""

        unique = set(batch.prompts)
        prev_size = len(self._dataset)
        self._dataset.update(unique)

        bt.logging.info(
            f"{len(batch.prompts)} prompts submitted. {len(unique)} unique prompts. "
            f"{len(self._dataset) - prev_size} new prompts"
        )

        self._submits.append(unique)
        self._latest.update(unique)

        bt.logging.info(f"{len(self._latest)} freshly minted prompts")

        while len(self._submits) > 0 and len(self._latest) - len(self._submits[0]) > self._batch_size:
            oldest_submit = self._submits.popleft()
            self._latest = self._latest - oldest_submit

        bt.logging.info(f"{len(self._latest)} prompts after prunning the old ones")

        if self._last_backup_time + self._backup_interval < time.time():
            self._last_backup_time = time.time()
            self._backup()

    def get(self) -> TextPromptBatch:  # type: ignore
        """Return the newest prompts."""
        latest_available = len(self._latest)
        if latest_available > self._batch_size:
            return TextPromptBatch(prompts=list(self._latest)[: self._batch_size])

        r = list(self._dataset)
        random.shuffle(r)
        return TextPromptBatch(prompts=list(self._latest) + r[: self._batch_size - latest_available])

    def _load_default_prompts(self, path: Path) -> None:
        if not path.exists():
            raise RuntimeError(f"Dataset file {path} not found")

        with path.open() as f:
            self._dataset = set(f.read().strip().split("\n"))

        bt.logging.info(f"{len(self._dataset)} prompts loaded")

    def _backup(self) -> None:
        cur_time = int(time.time())
        file_name = f"prompts_{cur_time}.txt"
        dataset_path = self._resource_dir / file_name
        thread = threading.Thread(target=self._perform_backup, args=(dataset_path, copy.copy(self._dataset)))
        thread.start()

    def _perform_backup(self, dataset_path: Path, data: set[str]) -> None:
        with dataset_path.open("w") as f:
            for prompt in data:
                f.write(prompt + "\n")


text_prompt_manager = TextPromptManager(
    resources_dir=Path(config.text_resource_dir),
    batch_size=config.text_prompt_batch_size,
    backup_interval=config.backup_interval,
)
# todo check resources path
