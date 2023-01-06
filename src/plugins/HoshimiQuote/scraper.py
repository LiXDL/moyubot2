import aiohttp
import asyncio
import lxml
from bs4 import BeautifulSoup
from datetime import datetime


async def get_daily() -> dict[str, str] | None:
    today = datetime.utcnow()
    async with aiohttp.ClientSession() as session:
        session.cookie_jar.clear()
        async with session.get(f"https://zh.wikiquote.org/zh-cn/Wikiquote:每日名言/{today.month}月{today.day}日") as response:
            text = (await response.read()).decode("utf-8")

    page = BeautifulSoup(text, "lxml")
    quote_section = page.find("div", attrs={"class": "mw-parser-output"})
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