import aiofiles
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from nonebot import on_command, require, get_bot
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


ACTOR = Path(__file__).resolve().parent / "ActorBirthday.json"
CHARA = Path(__file__).resolve().parent / "CharaBirthday.json"


BD_MONTH_HELP_MESSAGE = "\n".join([
    "查询给定月份的生日，默认查询本月生日",
    "/bd.month|本月生日 [月份(1-12)] [-h]"
])


month_birthday = on_command("bd.month", aliases={"本月生日"}, priority=20)
month_parser = argparse.ArgumentParser(prog="BD_Month", add_help=False)
month_parser.add_argument("month", nargs="?", default=0)
month_parser.add_argument("-h", "--help", action="store_true")


@month_birthday.handle()
async def month_bd_handler(cmd_args: Message = CommandArg()):
    args = month_parser.parse_args(cmd_args.extract_plain_text().strip().split())

    if args.help:
        await month_birthday.finish(BD_MONTH_HELP_MESSAGE)

    if not args.month:
        result = await get_month_bd()
    else:
        try:
            spec_month = int(args.month)
        except:
            await month_birthday.finish("非法参数，请重试！")
            
        if spec_month not in list(range(13)):
            await month_birthday.finish("未输入有效月份，请重试！")
    
        result = await(get_month_bd(spec_month))

    actor_bd, chara_bd = result[0], result[1]
    if not actor_bd and not chara_bd:
        #   Techinically this should not happen though?
        #   There should be someone's birthday each month.
        await month_birthday.finish("本月无角色或中之人生日")
    else:
        result_message = ""
        if chara_bd:
            chara_bd_text = "\n".join(map(
                lambda d: "{} ({}月{}日)".format(d["name"], d["birthday"]["month"], d["birthday"]["date"]),
                chara_bd
            ))
            result_message += "本月生日角色:\n{}".format(chara_bd_text)
        if actor_bd:
            actor_bd_text = "\n".join(map(
                lambda d: "{} ({}月{}日)".format(d["name"], d["birthday"]["month"], d["birthday"]["date"]),
                actor_bd
            ))
            if chara_bd:
                result_message += "\n"
            result_message += "本月生日中之人:\n{}".format(actor_bd_text)

        await month_birthday.finish(result_message)


@scheduler.scheduled_job("cron", hour=0, misfire_grace_time=3600)
async def daily_bd_notifier():
    actor_bd, chara_bd = await get_today_bd()
    if not actor_bd and not chara_bd:
        logger.info("Nobody's birthday today.")
        return
    
    today = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
    today_month, today_date = today.month, today.day

    result_message = ""

    if chara_bd:
        result_message += "过生日的角色是：{}".format(chara_bd[0])
    if actor_bd:
        if chara_bd:
            result_message += "\n"
        result_message += "过生日的中之人是：{}".format(actor_bd[0])

    result_message = "今天是{}月{}日，\n".format(today_month, today_date) + result_message
    bot = get_bot()
    await bot.send_group_msg(
        group_id=691014271,
        message=result_message
    )
    logger.info("There is someone's birthday today. Notification Message sent.")


@scheduler.scheduled_job("cron", day=1, misfire_grace_time=3600)
async def monthly_bd_notifier():
    actor_bd, chara_bd = await get_month_bd()

    if not actor_bd and not chara_bd:
        #   This is unlikely to happen, but just left here to avoid possible errors.
        logger.info("Nobody's birthday this month.")

    today = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
    today_month = today.month

    result_message = ""
    if chara_bd:
        chara_bd_text = "\n".join(map(
            lambda d: "{} ({}月{}日)".format(d["name"], d["birthday"]["month"], d["birthday"]["date"]),
            chara_bd
        ))
        result_message += "本月生日角色:\n{}".format(chara_bd_text)
    if actor_bd:
        actor_bd_text = "\n".join(map(
            lambda d: "{} ({}月{}日)".format(d["name"], d["birthday"]["month"], d["birthday"]["date"]),
            actor_bd
        ))
        if chara_bd:
            result_message += "\n"
        result_message += "本月生日中之人:\n{}".format(actor_bd_text)

    result_message = "到{}月了哦！\n".format(today_month) + result_message

    bot = get_bot()
    await bot.send_group_msg(
        group_id=691014271,
        message=result_message
    )
    logger.info("There are people's birthday this month. Notification Message sent.")


async def get_today_bd() -> tuple[list, list]:
    today = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
    today_month, today_date = today.month, today.day
    actor_result, chara_result = [], []
    async with aiofiles.open(ACTOR, "r") as af, aiofiles.open(CHARA, "r") as cf:

        actor_bd = json.loads(await af.read())
        chara_bd = json.loads(await cf.read())

        for actor in actor_bd:
            if actor["birthday"]["month"] == today_month and actor["birthday"]["date"] == today_date:
                actor_result.append(actor["name"])
        
        for chara in chara_bd:
            if chara["birthday"]["month"] == today_month and chara["birthday"]["date"] == today_date:
                chara_result.append(chara["name"])

    return actor_result, chara_result


async def get_month_bd(today_month: int = 0) -> tuple[list, list]:
    if not today_month:
        today = datetime.now(tz=ZoneInfo("Asia/Shanghai"))
        today_month = today.month

    actor_result, chara_result = [], []

    async with aiofiles.open(ACTOR, "r") as af, aiofiles.open(CHARA, "r") as cf:

        actor_bd = json.loads(await af.read())
        chara_bd = json.loads(await cf.read())

        for actor in actor_bd:
            if actor["birthday"]["month"] == today_month:
                actor_result.append(actor)
        
        for chara in chara_bd:
            if chara["birthday"]["month"] == today_month:
                chara_result.append(chara)

    actor_result = sorted(actor_result, key=lambda x: (x["birthday"]["date"], x["chara_id"]))
    chara_result = sorted(chara_result, key=lambda x: (x["birthday"]["date"], x["chara_id"]))
    return actor_result, chara_result