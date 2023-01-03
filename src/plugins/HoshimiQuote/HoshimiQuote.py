from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from nonebot import on_command, on_fullmatch, get_driver, get_bot, require
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .scraper import get_daily
from .utils import drawing
from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


check_botapi = on_command("check", permission=SUPERUSER)
daily_quote = on_fullmatch("星见语录", priority=10)


@check_botapi.handle()
async def _():
    test_image = plugin_config.base_image
    bot = get_bot()
    await bot.send_group_msg(
        group_id=111611379,
        message="测试文本\n[CQ:image,file={}]".format(test_image.resolve().as_uri())
    )
    await check_botapi.finish()


@daily_quote.handle()
async def daily_quote_handle():
    await daily_quote.send("等一下，我去帮你找她")

    cn_tz = ZoneInfo("Asia/Shanghai")
    today = datetime.today().astimezone(tz=cn_tz)
    today_str = today.strftime('%Y%m%d')

    target_img = plugin_config.output_path / f"{today_str}.png"
    
    if not target_img.is_file():
        quote_today = await get_daily()
        if not quote_today:
            await daily_quote.finish("👓星见同学说今天没找到名人名言")
        else:
            drawing(quote_today, f"{today_str}.png")
    
    msg = MessageSegment.text("👓星见同学说这是今天的名人名言哦\n") + MessageSegment.image(target_img)
    await daily_quote.finish(msg)


@scheduler.scheduled_job("cron", hour=9, misfire_grace_time=120)
async def daily_check():
    cn_tz = ZoneInfo("Asia/Shanghai")
    today = datetime.today().astimezone(tz=cn_tz)
    today_str = today.strftime('%Y%m%d')

    for i in range(7, 14):
        old_date = today - timedelta(days=i)
        old_date_str = old_date.strftime('%Y%m%d')

        old_img = plugin_config.output_path / f"{old_date_str}.png"

        old_img.unlink(missing_ok=True)

    today_img = plugin_config.output_path / f"{today_str}.png"
    if not today_img.is_file():
        quote_today = await get_daily()
        if not quote_today:
            await daily_quote.finish("👓星见同学说今天没找到名人名言")
        else:
            drawing(quote_today, f"{today_str}.png")

    bot = get_bot()
    await bot.send_group_msg(
        group_id=691014271,
        message="👓星见同学说这是今天的名人名言哦\n[CQ:image,file={}]".format(today_img.resolve().as_uri())
    )