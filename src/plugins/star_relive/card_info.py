import re
import argparse
from pathlib import Path

from nonebot import on_command, get_driver
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText, EventMessage
from nonebot.permission import SUPERUSER
from nonebot.utils import run_sync
from nonebot.typing import T_State

from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent

from .dto.Dress import Dress
from .util.converter import Converter
from .util.formatter import Formatter
from .util.downloader import batch_download
from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


CONFIRM = re.compile(r"^(y(es)?|n(o)?)$", re.IGNORECASE)
YES = re.compile(r"^y(es)?$", re.IGNORECASE)
NO = re.compile(r"^n(o)?$", re.IGNORECASE)
CID = re.compile(r"^\d{7}$")

FOWARD_ALIAS: dict
BACKWARD_ALIAS: dict

HELP_MESSAGE = "\n".join([
    "查卡器(beta 1.0):",
    "/card|查卡 7位卡牌ID [-h] [-a] [-q]",
    "-h, --help: 帮助信息",
    "-a, --all: 显示完整卡牌信息",
    "-q, --quit: 终止查询"
])


#   ArgParsers
card_parser = argparse.ArgumentParser(prog="Card", add_help=False)
card_parser.add_argument("cid", nargs="?")
card_parser.add_argument("-a", "--all", action="store_true")
card_parser.add_argument("-h", "--help", action="store_true")
card_parser.add_argument("-q", "--quit", action="store_true")


download = on_command("download", permission=SUPERUSER, priority=1)
showcard = on_command("card", aliases={"card", "查卡"}, priority=10)
alias = on_command("alias", aliases={"alias", "简称"}, priority=10)


@driver.on_startup
async def init_alias():
    global FOWARD_ALIAS, BACKWARD_ALIAS
    FOWARD_ALIAS = await Converter.load(plugin_config.resource_path / "alias.json")

    BACKWARD_ALIAS = {}
    for cid, card in FOWARD_ALIAS["root"].items():
        name, alias = card["name"], card["alias"]
        for a in alias:
            if not BACKWARD_ALIAS.get(a, None):
                BACKWARD_ALIAS[a] = []
            BACKWARD_ALIAS[a].append((cid, name))


@driver.on_shutdown
async def persis_alias():
    global FOWARD_ALIAS, BACKWARD_ALIAS
    reverse_map = {}
    for (a, cards) in BACKWARD_ALIAS.items():
        for card in cards:
            cid, name = card[0], card[1]
            if cid not in reverse_map:
                reverse_map[cid] = {"name": name, "alias": []}
            reverse_map[cid]["alias"].append(a)
    FOWARD_ALIAS = {"root": reverse_map}
    await Converter.persist(FOWARD_ALIAS, plugin_config.resource_path / "alias.json")


#   Download data from API
@download.handle()
async def download_handle_first_receive(args: Message = CommandArg()):
    force_rewrite = args.extract_plain_text()
    if not force_rewrite:
        updated_entries = await batch_download()
        await download.finish(f"Updated {updated_entries} records.")
    else:
        if force_rewrite != "rewrite":
            await download.finish(f"Invalid argument '{force_rewrite}'")
        else:
            await download.pause("Confirm force-rewriting current data?")


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


#   Search for card info
@showcard.handle()
async def showcard_handle_first_receive(matcher: Matcher, extra_args: T_State, cmd_args: Message = CommandArg()):
    args, rem_args = card_parser.parse_known_args(cmd_args.extract_plain_text().strip().split())

    if rem_args:
        await showcard.send("可能存在多余参数：{}".format(str(rem_args)))

    if args.help:
        await showcard.finish(HELP_MESSAGE)

    extra_args["full"] = args.all
    if args.cid:
        matcher.set_arg("cmd_args", cmd_args)


@showcard.got("cmd_args", prompt="请提供卡牌ID")
async def showcard_handle_cid(bot: Bot, event: GroupMessageEvent, extra_args: T_State, cmd_args: str = ArgPlainText("cmd_args")):
    args, rem_args = card_parser.parse_known_args(cmd_args.strip().split())

    if rem_args:
        await showcard.send("可能存在多余参数：{}".format(str(rem_args)))

    # #   'all' flag gets true as long as user specified it once
    all_flag = args.all or extra_args["full"]

    if not args.cid and args.quit:
        await showcard.finish("查询终止", at_sender=True)

    if not re.match(CID, args.cid):
        #   Invalid card id
        await showcard.reject(f"无效卡牌ID：'{args.cid}'；请重新输入！")

    card_path: Path
    if not (card_path := plugin_config.json_storage / f"{args.cid}.json").is_file():
        await showcard.finish(f"不存在卡牌：'{args.cid}'；查询终止")
    else:
        card_img = plugin_config.dress_image / f"{args.cid}.png"
        img_msg = MessageSegment.image(card_img)

        dress = await Formatter.json2dto(card_path)
        if not all_flag:
            info_text = await dress_summary_wrapper(dress)
            info_msg = MessageSegment.text("\n\n" + info_text)
            await showcard.finish(img_msg + info_msg, at_sender=True)
        else:
            info_texts = await dress_full_wrapper(dress)
            await bot.send_group_forward_msg(
                group_id=event.group_id, 
                messages=[{
                    "type": "node",
                    "data": {
                        "name": "胡蝶静羽",
                        "uin": event.self_id,
                        "content": [{
                            "type": "text",
                            "data": {"text": info_text}
                        }]
                    }
                } for info_text in info_texts]
            )
            await showcard.finish(img_msg, at_sender=True)


@run_sync
def dress_summary_wrapper(dress: Dress) -> str:
    return dress.summary()


@run_sync
def dress_full_wrapper(dress: Dress) -> list[str]:
    return dress.full()


@alias.handle()
async def alias_handle_first_receive(args)