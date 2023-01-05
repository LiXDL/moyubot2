import re
import argparse
from pathlib import Path
import pandas as pd

from nonebot import on_command, get_driver, require
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText, EventMessage
from nonebot.permission import SUPERUSER
from nonebot.utils import run_sync
from nonebot.typing import T_State

from nonebot.adapters.onebot.v11 import (
    Bot, Message, MessageSegment, GroupMessageEvent,
    GROUP_OWNER, GROUP_ADMIN
)

from .dto.Dress import Dress
from .util.converter import Converter
from .util.downloader import batch_download
from .config import Config

from . import AliasManager as AM
from . import DressManager as DM

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


CONFIRM = re.compile(r"^(y(es)?|n(o)?)$", re.IGNORECASE)
YES = re.compile(r"^y(es)?$", re.IGNORECASE)
NO = re.compile(r"^n(o)?$", re.IGNORECASE)
CID = re.compile(r"^\d{7}$")

ALIASES: pd.DataFrame

CARD_HELP_MESSAGE = "\n".join([
    "查卡器:",
    "默认输出数值信息，请添加参数以查看完整信息"
    "/card|查卡 7位卡牌ID|常用名 [-h] [-a] [-q]",
    "-h, --help: 帮助信息",
    "-a, --all: 完整卡牌信息（不支持多张查询，会增加被夹风险）",
    "-i, --image: 卡牌图片"
    "-q, --quit: 终止查询"
])

ALIAS_HELP_MESSAGE = "\n".join([
    "卡牌常用名管理:",
    "显示对应ID/常用名的卡牌的所有常用名"
    "/alias|常用名 *[7位卡牌ID|常用名] [-h] [-a]",
    "-h, --help: 帮助信息",
    "-a, --add: 添加常用名",
    "-r, --remove: 移除常用名(仅管理员可用)"
])

ALIAS_ADD_HELP_MESSAGE = "\n".join([
    "添加/移除常用名，参数: 7位卡牌ID 常用名",
    "7位卡牌ID必须为第一参数，支持同时添加/移除多个常用名，使用空格分隔",
    "示例: ",
    "/alias -a|-r 1090006 狗香 拉普耶斯香子",
    "本功能仅限管理员使用"
])


#   ArgParsers
download_parser = argparse.ArgumentParser(prog="Download", add_help=False)
download_parser.add_argument("-r", "--replace", action="store_true")

card_parser = argparse.ArgumentParser(prog="Card", add_help=False)
card_parser.add_argument("cid", nargs="+")
card_parser.add_argument("-a", "--all", action="store_true")
card_parser.add_argument("-i", "--image", action="store_true")
card_parser.add_argument("-h", "--help", action="store_true")
card_parser.add_argument("-q", "--quit", action="store_true")

alias_parser = argparse.ArgumentParser(prog="Alias", add_help=False)
alias_parser.add_argument("cinfo", nargs="*")
alias_parser.add_argument("-a", "--add", action="store_true")
alias_parser.add_argument("-r", "--remove", action="store_true")
alias_parser.add_argument("-h", "--help", action="store_true")


download = on_command("download", aliases={"更新卡牌"}, permission=SUPERUSER, priority=1)
showcard = on_command("card", aliases={"card", "查卡"}, priority=10)
alias = on_command("alias", aliases={"alias", "常用名"}, priority=10)


@driver.on_startup
def init_alias():
    AM.load(plugin_config.card_alias)


@driver.on_shutdown
def persis_alias():
    DM.shutdown()
    AM.persist(plugin_config.card_alias)


@scheduler.scheduled_job(trigger="interval", hours=1, id="store_alias")
async def period_persis():
    AM.persist(plugin_config.card_alias)


#   Download data from API
@download.handle()
async def download_handle(cmd_args: Message = CommandArg()):
    args = download_parser.parse_args(cmd_args.extract_plain_text().strip().split())
    await download.send("正在更新数据库...")
    if not args.replace:
        updated_entries = await batch_download()

        if updated_entries:
            await download.send(f"Updated {len(updated_entries)} records.")
            new_cards = "\n".join("新增卡牌: ({}, {})".format(*t) for t in updated_entries)
            AM.persist(plugin_config.card_alias)
            await download.finish(new_cards)
        else:
            await download.finish("无新增卡牌")
    else:
        updated_entries = await batch_download(force_rewrite=True)
        AM.persist(plugin_config.card_alias)
        await download.finish(f"Updated {len(updated_entries)} records.")

'''
@download.handle()
async def download_handle_params(args: Message = EventMessage()):
    confirmation = args.extract_plain_text()
    if not CONFIRM.match(confirmation):
        await download.reject(f"Invalid confirmation '{confirmation}'")
    else:
        if NO.match(confirmation):
            await download.finish("Downloading aborted.")
        else:
            await download.send("Start downloading, force-rewrite enabled.")
            updated_entries = await batch_download(force_rewrite=True)
            await download.finish(f"Updated {updated_entries} records.")
'''

#   Search for card info
@showcard.handle()
async def showcard_handle_first_receive(
    matcher: Matcher, 
    extra_args: T_State,
    cmd_args: Message = CommandArg()
):
    args, rem_args = card_parser.parse_known_args(cmd_args.extract_plain_text().strip().split())

    #   This one is no longer used
    #   Search for names/alias now allow space character contained.
    if rem_args:
        await showcard.send("可能存在多余参数：{}".format(str(rem_args)))

    if args.help:
        await showcard.finish(CARD_HELP_MESSAGE)

    extra_args["all_flag"] = args.all

    if args.cid:
        matcher.set_arg("cmd_args", cmd_args)


@showcard.got("cmd_args", prompt="请提供卡牌ID或常用名，以及其它参数")
async def showcard_handle_cid(
    bot: Bot, 
    extra_args: T_State,
    event: GroupMessageEvent, 
    cmd_args: str = ArgPlainText("cmd_args")
):
    args, rem_args = card_parser.parse_known_args(cmd_args.strip().split())

    #   This one is no longer used
    #   Search for names/alias now allow space character contained.
    if rem_args:
        await showcard.send("可能存在多余参数：{}".format(str(rem_args)))

    if not args.cid and args.quit:
        await showcard.finish("查询终止", at_sender=True)

    # if not re.match(CID, args.cid):
    #     #   Invalid card id
    #     await showcard.reject(f"无效卡牌ID：'{args.cid}'；请重新输入！")

    all_flag = args.all or extra_args["all_flag"]

    search_key = " ".join(args.cid)

    if re.match(CID, search_key):
        cards_2b_searched = [await AM.retrive_id(int(search_key))]
    else:
        cards_2b_searched = await AM.retrive_info(Converter.simplify(search_key))

    if all_flag and len(cards_2b_searched) > 1:
        # await showcard.reject("不支持同时查询多张卡牌完整信息，会增加被夹风险")
        await showcard.reject("\n".join([
            "不支持同时查询多张卡牌完整信息，会增加被夹风险",
            "请从常用名对应的卡牌ID中选择一个查询:",
            "; ".join([
                "({},{})".format(cinfo.cid, cinfo.cname) for cinfo in cards_2b_searched
            ])
        ]))

    if cards_2b_searched[0].status == 500:
        await showcard.finish("数据库好像噶了，快把歌卫兵请过来！")

    if cards_2b_searched[0].status == 404:
        await showcard.finish(f"不存在卡牌：'{args.cid}'；查询终止")

    if len(cards_2b_searched) == 1 and all_flag:
        #   Single full search
        target_cid = cards_2b_searched[0].cid
        target_alias = cards_2b_searched[0].calias

        card_img = plugin_config.dress_image / f"{target_cid}.png"

        dress = await DM.get_dress(target_cid)

        info_texts = await dress_full_wrapper(dress)
        await bot.send_group_forward_msg(
            group_id=event.group_id, 
            messages=[
                {
                    "type": "node",
                    "data": {
                        "name": "胡蝶静羽",
                        "uin": event.self_id,
                        "content": "[CQ:image,file={}]".format(card_img.resolve().as_uri())
                    }
                },
                {
                    "type": "node",
                    "data": {
                        "name": "胡蝶静羽",
                        "uin": event.self_id,
                        "content": "\n".join([
                            "卡牌ID: {}".format(target_cid),
                            "常用名: {}".format(str(target_alias))
                        ])
                    }
                },
                *[{
                    "type": "node",
                    "data": {
                        "name": "胡蝶静羽",
                        "uin": event.self_id,
                        # "content": [{
                        #     "type": "text",
                        #     "data": {"text": info_text}
                        # }]
                        "content": info_text
                    }
                } for info_text in info_texts]
            ]
        )
        await showcard.finish()

    #   Multiple simple search
    info_blocks: list[tuple[Path, str]] = []
    for cinfo in cards_2b_searched:
        target_cid = cinfo.cid

        card_img = plugin_config.dress_image / f"{target_cid}.png"

        if args.image:
            info_blocks.append((card_img, ""))
        else:
            dress = await DM.get_dress(target_cid)
            card_text = await dress_summary_wrapper(dress)

            info_blocks.append((card_img, "\n\n" + card_text))

    if len(info_blocks) == 1:
        await showcard.finish(Message(MessageSegment.image(info_blocks[0][0])).append(info_blocks[0][1]))
    else:
        await bot.send_group_forward_msg(
            group_id=event.group_id, 
            messages=[
                *[{
                    "type": "node",
                    "data": {
                        "name": "胡蝶静羽",
                        "uin": event.self_id,
                        "content": "[CQ:image,file={}]{}".format(
                            info_block[0].resolve().as_uri(),
                            info_block[1]
                        )
                    }
                } for info_block in info_blocks]
            ]
        )
        await showcard.finish()


@run_sync
def dress_summary_wrapper(dress: Dress) -> str:
    return dress.summary()


@run_sync
def dress_full_wrapper(dress: Dress) -> list[str]:
    return dress.full()


@alias.handle()
async def alias_handle_first_receive(
    matcher: Matcher, 
    cmd_args: Message = CommandArg()
):
    args = alias_parser.parse_args(cmd_args.extract_plain_text().strip().split())
    
    if not args.cinfo:
        if args.help:
            if args.add or args.remove:
                await alias.finish(ALIAS_ADD_HELP_MESSAGE)
            else:
                await alias.finish(ALIAS_HELP_MESSAGE)

        #   No information is given, need to prompt for further input
    else:
        #   Some infomation is given
        matcher.set_arg("cmd_args", cmd_args)


@alias.got("cmd_args", prompt="请输入常用名功能所需参数")
async def alias_handle_info(
    bot: Bot,
    event: GroupMessageEvent,
    cmd_args: str = ArgPlainText("cmd_args")
):
    args = alias_parser.parse_args(cmd_args.strip().split())
    if not args.cinfo:
        await alias.reject("未输入有效卡牌ID或常用名，请重试！")

    if not (args.add or args.remove):
        #   Display aliases
        if len(args.cinfo) > 5:
            await alias.finish("搜索内容过多，请勿超出5个")

        result = []
        for c in args.cinfo:
            if re.match(CID, c):
                current_card = await AM.retrive_id(int(c))
                if current_card.status == 500:
                    await alias.finish("数据库好像噶了，快把歌卫兵请过来！")
                
                if current_card.status == 404:
                    result.append("未找到卡牌{}的常用名".format(c))
                else:
                    #   status code 200 OK
                    result.append("\n".join([
                        "卡牌ID: {}".format(c),
                        "卡牌名称: {}".format(current_card.cname),
                        "常用名: {}".format(str(current_card.calias))
                    ]))
            else:
                simplified_c = Converter.simplify(c)
                current_cards = await AM.retrive_info(simplified_c)

                for current_card in current_cards:
                    if current_card.status == 500:
                        await alias.finish("数据库好像噶了，快把歌卫兵请过来！")
                    
                    if current_card.status == 404:
                        result.append("未找到'{}'的对应卡牌".format(c))
                    else:
                        #   status code 200 OK
                        result.append("\n".join([
                            "卡牌ID: {}".format(c),
                            "卡牌名称: {}".format(current_card.cname),
                            "常用名: {}".format(str(current_card.calias))
                        ]))

        result_text = "\n\n".join(["搜索结果:", *result])
        await alias.finish(result_text)
    else:
        if args.remove and not (
            await GROUP_OWNER(bot, event) or 
            await GROUP_ADMIN(bot, event)
        ):
            await alias.finish("仅群管理可使用常用名移除功能")

        if args.add and args.remove:
            #   Conflict arguments
            await alias.finish("参数冲突！\n请勿同时使用添加/移除命令")

        cid = args.cinfo[0]
        target_aliases = list(map(Converter.simplify, args.cinfo[1:]))

        if not re.match(CID, cid):
            await alias.reject(f"无效卡牌ID：'{cid}'；请重新输入！")
        cid = int(cid)

        if not (plugin_config.dress_json / f"{cid}.json").is_file():
            await alias.finish(f"不存在卡牌：'{args.cid}'；操作终止")

        if not target_aliases:
            await alias.finish(f"未提供常用名；操作终止")

        if args.add:
            adding_result = await AM.add_alias(cid, target_aliases)
            
            if adding_result.status == 500:
                await alias.finish("数据库好像噶了，快把歌卫兵请过来！")
            if adding_result.status == 404:
                await alias.finish(f"卡牌{cid}尚未创建常用名记录，歌卫兵全责")

            #   Status code 200 OK
            await alias.finish("\n".join([
                "已为卡牌{}添加常用名:\n{}".format(cid, str(target_aliases)),
                "现有常用名:\n{}".format(str(adding_result.calias))
            ]))
        else:   #   args.remove
            removing_result = await AM.remove_alias(cid, target_aliases)

            if removing_result.status == 500:
                await alias.finish("数据库好像噶了，快把歌卫兵请过来！")
            if removing_result.status == 404:
                await alias.finish(f"卡牌{cid}尚未创建常用名记录，歌卫兵全责")

            await alias.finish("\n".join([
                "已从卡牌{}移除常用名:\n{}".format(cid, str(target_aliases)),
                "现有常用名:\n{}".format(str(removing_result.calias))
            ]))
