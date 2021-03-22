from typing import Optional, Tuple

from pydantic import BaseModel, HttpUrl


class Organic(BaseModel):
    display_path: str
    title: str
    url: HttpUrl
    description: Optional[str]


class Adword(BaseModel):
    visual_url: Optional[str]
    title: Optional[str]
    description: Optional[str]


class MapsSidebar(BaseModel):
    title: str
    website: Optional[HttpUrl]
    company_type: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    gesloten: Optional[str]
    # voor restaurants
    checks: Optional[list[Tuple[str, bool]]]
    bestellen: Optional[list[str]]
    # voor hotels
    hoteldvoorzieningen: Optional[list[str]]


class Serp(BaseModel):
    serp_url: str
    organic_results: list[Organic]
    adwords: list[Adword]
    related: list[str]
    maps_sidebar: Optional[MapsSidebar]


class Query(BaseModel):
    query: str
    serps: list[Serp]
