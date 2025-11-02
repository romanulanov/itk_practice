import asyncio
import aiohttp
import aiofiles
import argparse
import json
from typing import Any, Dict


async def fetch_json(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
            response.raise_for_status()
            try:
                data = await asyncio.get_event_loop().run_in_executor(None, lambda: asyncio.run(response.json()))
            except aiohttp.ContentTypeError:
                return {"url": url, "content": None}
            return {"url": url, "content": data}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return {"url": url, "content": None}


async def worker(
    name: int,
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    output_file: str,
):
    async with aiofiles.open(output_file, "a") as out:
        while True:
            url = await queue.get()
            if url is None:
                queue.task_done()
                break
            result = await fetch_json(session, url)
            json_line = await asyncio.get_event_loop().run_in_executor(
                None, lambda: json.dumps(result, ensure_ascii=False)
            )
            await out.write(json_line + "\n")
            queue.task_done()


async def fetch_urls(input_file: str, output_file: str):
    queue = asyncio.Queue(maxsize=100)

    connector = aiohttp.TCPConnector(limit=10, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        workers = [
            asyncio.create_task(worker(i, queue, session, output_file))
            for i in range(5)
        ]

        async with aiofiles.open(input_file, "r") as f:
            async for line in f:
                url = line.strip()
                if url:
                    await queue.put(url)

        await queue.join()

        for _ in range(5):
            await queue.put(None)

        await asyncio.gather(*workers)


def main():
    parser = argparse.ArgumentParser(
        description="Асинхронно скачивает JSON-ответы по списку URL и сохраняет в JSONL"
    )
    parser.add_argument("input", help="Файл со списком URL (по одному в строке)")
    parser.add_argument("output", help="Файл для записи результатов (JSONL)")
    args = parser.parse_args()

    asyncio.run(fetch_urls(args.input, args.output))


if __name__ == "__main__":
    main()
