import asyncio
from aiofiles import open as aioopen
import argparse
import aiohttp
import json


async def fetch_json(
        session: aiohttp.ClientSession,
        url: str, sem: asyncio.Semaphore
        ):
    async with sem:
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        return {"url": url, "content": None}
                    return {"url": url, "content": data}
                else:
                    return {"url": url, "content": None}
        except asyncio.TimeoutError:
            return {"url": url, "content": None}
        except aiohttp.ClientError:
            return {"url": url, "content": None}


async def fetch_urls(input_file: str, output_file: str):
    async with aioopen(input_file, "r") as f:
        urls = []
        for line in await f.readlines():
            if line.strip():
                urls.append(line.strip())

    sem = asyncio.Semaphore(5)

    connector = aiohttp.TCPConnector(limit=10, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        async with aioopen(output_file, "w") as out:
            for url in urls:
                tasks.append(fetch_json(session, url, sem))

            for future in asyncio.as_completed(tasks):
                result = await future
                await out.write(json.dumps(result, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser("Скачивает асинхронно из файла со списком\
                                    URL JSON-ответы и сохраняет в JSONL")
    parser.add_argument("input", help="Файл со списком URL-адресов (по одному\
                        в строке)")
    parser.add_argument("output", help="Файл, куда записать результаты \
                        (JSONL)")
    args = parser.parse_args()

    asyncio.run(fetch_urls(args.input, args.output))


if __name__ == "__main__":
    main()
