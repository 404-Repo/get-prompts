import asyncio
from pathlib import Path

import httpx


def extract_filename_from_headers(headers: dict[str, str]) -> str | None:
    content_disposition = headers.get("content-disposition", "")
    if "attachment" in content_disposition:
        return content_disposition.replace("attachment; filename=", "")
    return None


async def download_file_from_external_server(url: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=100000)
        response.raise_for_status()  # Check for HTTP errors

        save_path = Path("temp/tests")
        save_path.mkdir(parents=True, exist_ok=True)

        print(response.headers)
        filename = extract_filename_from_headers(response.headers)
        if filename is not None:
            filepath = Path(save_path) / filename
            with filepath.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
            print(f"File saved at {save_path}")


async def test_multiple_concurrent_downloads() -> None:
    tasks = [download_file_from_external_server("http://localhost:8093/images/download") for _ in range(20)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(test_multiple_concurrent_downloads())
    print("All downloads completed! ✅")
