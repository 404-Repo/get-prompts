import random as rd
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path

from main.exceptions import NoDefaultImagePrompts

from utils.schemas.image_data import ImageData


class BaseImageStorage(ABC):

    @abstractmethod
    def get(self, *, batch_size: int) -> Iterable[ImageData]:
        pass

    @abstractmethod
    def add(self, *, images: list[ImageData]) -> None:
        pass


class DiskImageStorage(BaseImageStorage):
    def __init__(self, *, resources_dir: Path, min_default_file_cnt: int) -> None:
        self._resources_dir = resources_dir
        if not self._resources_dir.exists():
            raise NoDefaultImagePrompts(f"{self._resources_dir} does not exist.")
        file_cnt = sum(1 for f in self._resources_dir.iterdir() if f.is_file())
        if file_cnt < min_default_file_cnt:
            raise NoDefaultImagePrompts(
                f"There are {file_cnt} default images available "
                f"that is less than minimal amount {min_default_file_cnt}."
            )

    def get(self, *, batch_size: int) -> Iterable[ImageData]:
        image_datas: list[ImageData] = []
        file_paths = [f for f in self._resources_dir.iterdir()]
        selected_file_paths = rd.sample(file_paths, batch_size)
        for file_path in selected_file_paths:
            with file_path.open("rb") as f:
                data = BytesIO(f.read())
                image_datas.append(
                    ImageData(
                        data=data,
                        filename=file_path.name,
                    )
                )

        return image_datas

    def add(self, *, images: list[ImageData]) -> None:
        raise NotImplementedError()


class InMemoryImageStorage(BaseImageStorage):
    def __init__(self, *, max_image_cnt: int) -> None:
        self._max_image_cnt = max_image_cnt
        self._images: deque[ImageData] = deque()
        self._filenames: set[str] = set()

    def get(self, *, batch_size: int) -> Iterable[ImageData]:
        if len(self._images) < self._max_image_cnt:
            return rd.sample(self._images, batch_size)
        return self._images

    def add(self, *, images: list[ImageData]) -> None:
        unique_images = filter(lambda im: im.filename not in self._filenames, images)
        unique_image_cnt = sum(1 for _ in unique_images)
        total_cnt = unique_image_cnt + len(self._images)
        if total_cnt > self._max_image_cnt:
            for _ in range(total_cnt - self._max_image_cnt):
                im = self._images.popleft()
                self._filenames.remove(im.filename)
        self._images.extend(unique_images)
        self._filenames.update(im.filename for im in unique_images)
