import asyncio
import aiofiles
import aiohttp
from itertools import product

try:
    import ujson as json
except:
    import json

from nonebot import get_driver
from nonebot.log import logger

from ..config import Config, DownloadCofig
from .. import AliasManager as AM
from .. import DressManager as DM

from .converter import Converter

plugin_config = Config.parse_obj(get_driver().config)


async def batch_download(force_rewrite=False) -> list:
    ids = list(map(
        lambda t: str(int(t[0] * 10e5 + t[1] * 10e3 + t[2])),
        product(DownloadCofig["school"], DownloadCofig["max_character"], DownloadCofig["limit"])
    ))
    ids = ids + list(map(str, DownloadCofig["special_event"]))

    sema = asyncio.BoundedSemaphore(10)

    # tasks = [single_download(id, sema, force_rewrite) for id in ids]
    # download_result = await asyncio.gather(*tasks)
    async with sema, aiohttp.ClientSession() as session:
        download_result = await asyncio.gather(*[single_download(id, session, force_rewrite) for id in ids])

    valid_download_result = list(filter(lambda c: c is not None, download_result))
    return valid_download_result


async def single_download(identifier: str, session: aiohttp.ClientSession, force_rewrite=False) -> tuple[int, str] | None:
    data_target = plugin_config.dress_json / f"{identifier}.json"
    image_target = plugin_config.dress_image / f"{identifier}.png"

    #   Already exists
    if data_target.is_file() and not force_rewrite:
        return None

    data_url = plugin_config.api_dress + f"/{identifier}.json"
    image_url = plugin_config.api_image + f"/{identifier}/image.png"

    async with session.get(data_url) as data_source, session.get(image_url) as image_source:
        if data_source.status != 200:
            #   Usually 404 not found
            return None
        else:
            raw_data = json.loads(await data_source.text(encoding="utf-8"))
            raw_image = await image_source.read()

    async with aiofiles.open(data_target, "w") as data_afp, aiofiles.open(image_target, "wb") as image_afp:
        await data_afp.write(json.dumps(raw_data, indent=4, ensure_ascii=False))
        await image_afp.write(raw_image)

    #   Add to 
    await DM.insert_dress(raw_data)
            
    cid = int(raw_data["basicInfo"]["cardID"])
    cname = str(raw_data["basicInfo"]["name"].get("zh_hant", raw_data["basicInfo"]["name"]["ja"]))

    await AM.add_card(cid, Converter.simplify(cname), Converter.simplify(cname))

    logger.info("Added card ({}, {})".format(cid, cname))

    return (cid, cname)
