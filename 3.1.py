import asyncio
import aiohttp
import json


async def fetch_url(session, url, sem):
    async with sem:
        try:
            async with session.get(url, timeout=10) as response:
                return {"url": url, "status_code": response.status}
        except Exception:
            return {"url": url, "status_code": 0}


async def fetch_urls(urls: list[str], file_path: str):
    sem = asyncio.Semaphore(5)
    results = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch_url(session, url, sem))
        for future in asyncio.as_completed(tasks):
            result = await future
            results.append(result)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")
    result = {}
    for r in results:
        result[r['url']] = r['status_code']
    return result


urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]

if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.jsonl'))
