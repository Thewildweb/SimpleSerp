# SimpleSerp

Library for scraping Google SERP. _Not yet ready for use in production._

## Example
```python
import asyncio

from simple_serp import get_browser, query_google

async def get_query(query):
    async with get_browser() as browser:
        results = await query_google("query", browser)

    return results

results = asyncio.run(get_query("example query"))
```

## Technologies

- Playwright
- Selectolax
- Pydantic

## TODO

- Replace the google_client function with a GoogleClient class
- Dynamicly create new context after a failed query
- Dynamicly get a new proxy after a failed query
- Write tests
- Parse Video
- Parse Images
- Parse LockalPack
- Parse Shopping
- Expand parsing adwords
- Expand parsing organic
- Expand parsing Knowledge-panel