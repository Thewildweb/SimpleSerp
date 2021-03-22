import asyncio
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from typing import Optional
import logging

from playwright.async_api._generated import Browser
from playwright.async_api import async_playwright

from .models import Query, Serp
from .parser import parse_html


@asynccontextmanager
async def get_client(proxy: Optional[dict]=None):
    async with async_playwright() as playwright:
        firefox = playwright.firefox  # or "firefox" or "webkit".
        browser = await firefox.launch(proxy=proxy)
        yield browser

        await browser.close()


async def get_page(url: str, browser: Browser) -> str:
    page = await browser.new_page()
    await page.goto(url)
    cont = await page.content()
    await page.close()

    return cont


async def query_google(
    query: str, browser: Browser, max_pages: int = 1, retries: int = 3
) -> str:
    return_query = Query(query=query, serps=[])
    # create query
    query = quote_plus(query)
    g_url = f"https://www.google.com/search?q={query}"

    for i in range(max_pages):
        offset = i * 10

        if offset > 0:
            g_url = f"{g_url}&start{offset}"

        try:
            cont = await get_page(g_url, browser)
        except Exception as e:
            if retries > 0:
                logging.warning(f"Error with: {g_url}")
                retries -= 1
                cont = await query_google(query, browser, retries)
            else:
                logging.warning(
                    f"Maximum retries for querie: {query}. Offset: {offset}. Url: {g_url}. Error: {e}"
                )
                break

        try:
            parsed = parse_html(cont)
        except Exception as e:
            logging.warning(f"Error in parsing")
            break

        serp = Serp(
            serp_url=g_url,
            organic_results=parsed["organic_results"],
            adwords=parsed["adwords_results"],
            related=parsed["related"],
            maps_sidebar=parsed["maps_sidebar"],
        )
        return_query.serps.append(serp)

    return return_query