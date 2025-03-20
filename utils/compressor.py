import asyncio
import struct
from abc import ABC, abstractmethod
from pathlib import Path

from zstandard import ZstdCompressor


class CompressorBase(ABC):

    @staticmethod
    @abstractmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def decompress(*, archive: Path, output_dir: Path) -> None:
        pass


class ZstandardCompressor(CompressorBase):
    _COMPRESSION_LEVEL: int = 9

    @staticmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        await asyncio.to_thread(
            ZstandardCompressor._compress_files, files, archive_path, ZstandardCompressor._COMPRESSION_LEVEL
        )

    @staticmethod
    async def decompress(*, archive: Path, output_dir: Path) -> None:
        pass

    @staticmethod
    def _compress_files(files: list[Path], archive_path: Path, level: int) -> None:
        # todo Handle errors
        with archive_path.open("wb") as f_out:
            compressor = ZstdCompressor(level=level)
            with compressor.stream_writer(f_out) as zstd_writer:
                for file_path in files:
                    data = file_path.read_bytes()
                    filename = file_path.name.encode()  # Store filename

                    # Write filename length (4 bytes) + filename + file size (4 bytes) + file data
                    zstd_writer.write(struct.pack("I", len(filename)) + filename)
                    zstd_writer.write(struct.pack("I", len(data)) + data)
