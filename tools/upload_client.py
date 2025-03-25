import asyncio
import random
from pathlib import Path

import aiofiles  # type: ignore
import faker
import httpx
import msgpack


fake = faker.Faker()


def get_file_cnt(file_dir: Path) -> int:
    return sum(1 for f in file_dir.iterdir())


async def send_message_pack(file_dir: Path) -> None:
    async with httpx.AsyncClient() as client:
        files_data = []
        file_cnt = sum(1 for f in file_dir.iterdir())
        print(f"{file_dir} contains {file_cnt} files")

        for file in file_dir.iterdir():
            async with aiofiles.open(file, "rb") as f:
                file_data = await f.read()
                files_data.append({"normalized_prompt": fake.sentence(), "data": file_data})

        packed_data = msgpack.packb(files_data, use_bin_type=True)
        files = {"file": ("packed_files.msgpack", packed_data, "application/octet-stream")}
        response = await client.post("http://localhost:8093/images/submit", files=files, timeout=100000)

        if response.status_code == 200:
            print("Response received")
        else:
            print(f"Error: {response.status_code}, {response.text}")


async def main() -> None:
    async with httpx.AsyncClient():
        dirs = [dir for dir in Path("temp").iterdir() if get_file_cnt(dir) > 1000]
        tasks = [send_message_pack(dir) for dir in random.sample(dirs, 10)]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)


# Run the main function to start the upload process
if __name__ == "__main__":
    asyncio.run(main())
