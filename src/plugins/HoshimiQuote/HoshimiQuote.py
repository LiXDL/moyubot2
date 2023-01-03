from datetime import datetime
from zoneinfo import ZoneInfo

from nonebot import on_keyword, on_fullmatch, get_driver, require
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .scraper import get_daily
from .utils import drawing
from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


daily_quote = on_fullmatch("星见语录", priority=10)


@daily_quote.handle()
async def daily_quote_handle():
    await daily_quote.send("等一下，我去帮你找她")

    cn_tz = ZoneInfo("Asia/Shanghai")
    today = datetime.today().astimezone(tz=cn_tz)
    today_str = today.strftime('%Y%m%d')

    target_img = plugin_config.output_path / f"{today_str}.png"
    
    if not target_img.is_file():
        quote_today = await get_daily()
        await daily_quote.send("")
        if not quote_today:
            await daily_quote.finish("👓星见同学说今天没找到名人名言")
        else:
            drawing(quote_today, f"{today_str}.png")
    
    msg = MessageSegment.text("👓星见同学说这是今天的名人名言哦\n") + MessageSegment.image(target_img)
    await daily_quote.finish(msg)
