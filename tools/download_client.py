import asyncio
from pathlib import Path
from random import randint

import aiofiles  # type: ignore
import httpx
import msgpack


async def unpack_message_pack_stream(url: str) -> None:
    dir_name = f"{randint(0,10000)}"  # noqa: S311

    async with httpx.AsyncClient() as client:
        unpacker = msgpack.Unpacker(raw=False)
        async with client.stream("GET", url) as response:
            if response.status_code != 200:
                return
            # Stream the data in chunks and process each chunk
            async for chunk in response.aiter_bytes():
                unpacker.feed(chunk)
                for data in unpacker:
                    normalized_prompt = data["normalized_prompt"]
                    data = data["data"]
                    # Save the image data to disk (ensure that normalized_prompts are safe)
                    dir_path = Path("temp") / dir_name
                    dir_path.mkdir(parents=True, exist_ok=True)
                    file_path = dir_path / f"{normalized_prompt}.txt"

                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(data)


async def main() -> None:
    async with httpx.AsyncClient():
        url = "http://localhost:8093/images/download"

        # Create a list of tasks for concurrent fetching
        tasks = [unpack_message_pack_stream(url) for _ in range(100)]

        # Await all tasks to run concurrently
        await asyncio.gather(*tasks)


# Run the asynchronous main function
asyncio.run(main())
