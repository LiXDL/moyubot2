import aiohttp
import asyncio
import lxml
from bs4 import BeautifulSoup

'''
async def get_daily() -> dict[str, str] | None:
    async with aiohttp.ClientSession() as session:
        session.cookie_jar.clear()
        async with session.get("https://zh.wikiquote.org/zh-cn/Wikiquote:每日名言") as response:
            text = (await response.read()).decode("utf-8")

    page = BeautifulSoup(text, "lxml")
    quote_section = page.find("div", attrs={"style": "width:55%; background-color:#fff3f3; border:1px solid #ffc9c9;padding:1em;padding-top:0.5em; color: black"})
    try:
        texts = quote_section.find_all(text=True)
        quotes = list(filter(lambda c: c != "\n", texts))

        if not quotes:
            raise ValueError

        return {"quote": quotes[0][:-2], "by": quotes[1]}
    except:
        return None
'''

async def get_daily() -> dict[str, str] | None:
    async with aiohttp.ClientSession() as session:
        session.cookie_jar.clear()
        async with session.get("https://zh.wikiquote.org/zh-cn/Wikiquote:首页", headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}) as response:
            text = (await response.read()).decode("utf-8")

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
    result = asyncio.run(get_daily())
    print(result)