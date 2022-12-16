import re
from pathlib import Path

from nonebot import on_command, get_driver
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, ArgPlainText, CommandArg, EventMessage
from nonebot.permission import SUPERUSER

from nonebot.adapters.onebot.v11 import MessageSegment

from .util.formatter import Formatter
from .util.downloader import batch_download
from .config import Config


plugin_config = Config.parse_obj(get_driver().config)


CONFIRM = re.compile("^(y(es)?|n(o)?)$", re.IGNORECASE)
YES = re.compile("^y(es)?$", re.IGNORECASE)
NO = re.compile("^n(o)?$", re.IGNORECASE)


download = on_command("download", permission=SUPERUSER, priority=1)
showcard = on_command("showcard", priority=10)


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


@showcard.handle()
async def showcard_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    card_id = args.extract_plain_text()
    if card_id:
        matcher.set_arg("card", args)

@showcard.got("card", prompt="请提供卡牌ID")
async def showcard_handle_cardid(card: Message = Arg(), card_id: str = ArgPlainText("card")):
    if not (plugin_config.json_storage / f"{card_id}.json").is_file():
        await showcard.finish("找不到对象")
    else:
        card_info = plugin_config.json_storage / f"{card_id}.json"
        info_text = await Formatter.dict2text(
            await Formatter.dto2dict(
                await Formatter.json2dto(card_info)
            )
        )
        info_msg = MessageSegment.text("\n\n" + info_text)

        card_img = plugin_config.dress_image / f"{card_id}.png"
        img_msg = MessageSegment.image(card_img)

        await showcard.finish(img_msg + info_msg)
