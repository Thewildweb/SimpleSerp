import datetime
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from typing import Optional
import logging

from playwright.async_api._generated import Browser
from playwright.async_api import async_playwright

from .models import Query, Serp
from .parser import parse_html


class SorryError(Exception):
    """We raise this error when the sorry request url is requested"""


@asynccontextmanager
async def get_client():
    async with async_playwright() as playwright:
        chromium = playwright.firefox  # or "firefox" or "webkit".
        browser = await chromium.launch(proxy={"server": "per-context"})
        yield browser

        await browser.close()


async def routing(intercepted):
    if intercepted.request.url == "https://www.google.com/recaptcha/api.js":
        await intercepted.abort()
    elif intercepted.request.resource_type == "document":
        await intercepted.continue_()
    else:
        await intercepted.abort(),


async def get_page(
    url: str,
    browser: Browser,
    proxy: Optional[dict] = None,
    locale: Optional[str] = None,
    user_agent: Optional[str] = None,
    retries: int = 3,
    sorry_retries: int = 20,
) -> str:
    locs = locals()
    context_dict = {}
    if proxy:
        context_dict["proxy"] = proxy
    if locale:
        context_dict["locale"] = locale
    if user_agent:
        context_dict["user_agent"] = user_agent

    context = await browser.new_context(**context_dict)
    page = await context.new_page()

    await page.route("**/*", routing)

    try:
        await page.goto(url)
    except Exception as e:
        await context.close()
        if retries > 0:
            locs["retries"] -= 1
            return await get_page(**locs)
        raise e

    if "/sorry/" in page.url:
        if sorry_retries > 0:
            locs["sorry_retries"] -= 1
            return await get_page(**locs)
        raise SorryError

    try:
        cont = await page.content()
    except Exception as e:
        cont = None

    await context.close()

    return cont


async def query_google(
    query: str,
    browser: Browser,
    proxy: Optional[dict] = None,
    locale: Optional[str] = None,
    user_agent: Optional[str] = None,
    max_pages: int = 1,
    retries: int = 3,
    city: str = None,
    uule: str = None,
) -> str:
    return_query = Query(query=query, serps=[])
    # create query
    query = quote_plus(query)
    g_url = f"https://www.google.com/search?q={query}"

    if uule:
        g_url += uule

    for i in range(max_pages):
        offset = i * 10

        if offset > 0:
            g_url = f"{g_url}&start{offset}"

        try:
            cont = await get_page(
                g_url,
                browser,
                proxy=proxy,
                locale=locale,
                user_agent=user_agent,
                retries=retries,
            )
        except SorryError:
            logging.debug(f"Just got the SorryError, retrying")
            cont = await query_google(query, browser, retries=retries)
        except Exception as e:
            if retries > 0:
                logging.warning(f"Error with: {g_url}. Error {e}")
                retries -= 1
                cont = await query_google(query, browser, retries=retries)
            else:
                logging.warning(
                    f"Maximum retries for querie: {query}. Offset: {offset}. Url: {g_url}. Error: {e}"
                )
                break

        filename = f"code-{datetime.datetime.utcnow().timestamp()}.html"
        with open(filename, "w") as html_file:
            html_file.write(cont)

        try:
            parsed = parse_html(cont)
        except Exception as e:
            logging.warning(f"Error in parsing")
            break

        # TODO Redo failed parsed

        serp = Serp(
            serp_url=g_url,
            organic_results=parsed["organic_results"],
            adwords=parsed["adwords_results"],
            related=parsed["related"],
            maps_sidebar=parsed["maps_sidebar"],
        )
        return_query.serps.append(serp)

    return return_query
