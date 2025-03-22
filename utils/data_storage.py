import asyncio
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from io import BytesIO
from pathlib import Path
from typing import Generic, TypeVar

import aiofiles  # type: ignore
from main.exceptions import NoDefaultImagePrompts

from utils.schemas.image_data import ImageData


DataT = TypeVar("DataT")


class BaseDataStorage(ABC, Generic[DataT]):

    @abstractmethod
    def get(self, *, batch_size: int) -> list[DataT]:
        pass

    @abstractmethod
    def add(self, *, datas: list[DataT]) -> None:
        pass


class DiskTextStorage(BaseDataStorage[str]):
    def get(self, *, batch_size: int) -> list[str]:
        raise NotImplementedError()

    def add(self, *, datas: list[str]) -> None:
        raise NotImplementedError()


class DiskImageStorage(BaseDataStorage[ImageData]):
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

    async def get(self, *, batch_size: int) -> list[ImageData]:  # type: ignore
        file_paths = [f for f in self._resources_dir.iterdir()]
        selected_file_paths = rd.sample(file_paths, min(batch_size, len(file_paths)))

        async def read_file(file_path: Path) -> ImageData:
            async with aiofiles.open(file_path, "rb") as f:
                data = await f.read()
            return ImageData(data=BytesIO(data), filename=file_path.name)

        image_datas = await asyncio.gather(*(read_file(fp) for fp in selected_file_paths))
        return image_datas

    def add(self, *, datas: list[ImageData]) -> None:
        raise NotImplementedError()


class InMemoryImageStorage(BaseDataStorage[ImageData]):
    def __init__(self, *, max_image_cnt: int) -> None:
        self._max_image_cnt = max_image_cnt
        self._images: deque[ImageData] = deque()
        self._filenames: set[str] = set()

    def get(self, *, batch_size: int) -> list[ImageData]:
        if len(self._images) < self._max_image_cnt:
            return rd.sample(self._images, batch_size)
        return list(self._images)

    def add(self, *, datas: list[ImageData]) -> None:
        unique_images = (im for im in self._images if im.filename not in self._filenames)
        unique_image_cnt = sum(1 for _ in unique_images)
        total_cnt = unique_image_cnt + len(self._images)
        if total_cnt > self._max_image_cnt:
            for _ in range(total_cnt - self._max_image_cnt):
                im = self._images.popleft()
                self._filenames.remove(im.filename)
        self._images.extend(unique_images)
        self._filenames.update(im.filename for im in unique_images)
