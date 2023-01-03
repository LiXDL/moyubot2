import aiohttp
import asyncio
import lxml
from bs4 import BeautifulSoup, PageElement


async def get_daily() -> dict[str, str] | None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://zh.wikiquote.org/wiki/Wikiquote:%E9%A6%96%E9%A1%B5") as session:
            text = (await session.read()).decode("utf-8")

    page = BeautifulSoup(text, "lxml")
    quote_section = page.find(id="mp-everyday-quote")
    try:
        texts = quote_section.find_all(text=True)
        quotes = list(filter(lambda c: c != "\n", texts))

        if not quotes:
            raise ValueError

        return {"quote": quotes[0][:-2], "by": quotes[1]}
    except:
        return None
   

if __name__ == "__main__":
    pass