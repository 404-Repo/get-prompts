import asyncio
import struct
from abc import ABC, abstractmethod
from pathlib import Path

from zstandard import ZstdCompressor, ZstdDecompressor


class ArchiveManagerBase(ABC):

    @staticmethod
    @abstractmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def decompress(*, archive_path: Path, output_dir: Path) -> None:
        pass


class ZstandardManager(ArchiveManagerBase):
    _COMPRESSION_LEVEL: int = 9

    @staticmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        await asyncio.to_thread(
            ZstandardManager._compress_files, files, archive_path, ZstandardManager._COMPRESSION_LEVEL
        )

    @staticmethod
    async def decompress(*, archive_path: Path, output_dir: Path) -> None:
        await asyncio.to_thread(ZstandardManager._decompress_files, archive_path, output_dir)

    @staticmethod
    def _decompress_files(archive_path: Path, output_dir: Path) -> None:
        decompressor = ZstdDecompressor()
        with archive_path.open("rb") as sync_f:
            with decompressor.stream_reader(sync_f) as zstd_reader:
                while True:
                    filename_length_bytes = zstd_reader.read(4)
                    if not filename_length_bytes:
                        break
                    filename_length = struct.unpack("I", filename_length_bytes)[0]
                    filename = zstd_reader.read(filename_length).decode()
                    file_size = struct.unpack("I", zstd_reader.read(4))[0]
                    file_data = zstd_reader.read(file_size)
                    output_path = output_dir / filename
                    with output_path.open("wb") as out_file:
                        out_file.write(file_data)

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
