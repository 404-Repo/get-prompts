import asyncio
from pathlib import Path
from random import randint

import aiofiles  # type: ignore
import httpx
import msgpack


async def unpack_message_pack_stream(url: str) -> None:
    dir_name = f"{randint(0,10000)}"  # noqa: S311

    async with httpx.AsyncClient(timeout=10000) as client:
        unpacker = msgpack.Unpacker(raw=False)
        async with client.stream("GET", url) as response:
            if response.status_code != 200:
                return

            async for chunk in response.aiter_bytes():
                unpacker.feed(chunk)
                for data in unpacker:
                    data = data["data"]
                    dir_path = Path("temp") / dir_name
                    dir_path.mkdir(parents=True, exist_ok=True)
                    file_path = dir_path / f"{randint(0,1000000)}.webp"  # noqa: S311

                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(data)


async def main() -> None:
    async with httpx.AsyncClient():
        url = "http://localhost:8093/images/download"

        tasks = [unpack_message_pack_stream(url) for _ in range(20)]
        await asyncio.gather(*tasks)


# Run the asynchronous main function
asyncio.run(main())
