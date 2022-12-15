import os
import re

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg, EventMessage
from nonebot.permission import SUPERUSER

from .util.formatter import Formatter
from .util.downloader import batch_download


CONFIRM = re.compile("^(y(es)?|n(o)?)$", re.IGNORECASE)
YES = re.compile("^y(es)?$", re.IGNORECASE)
NO = re.compile("^n(o)?$", re.IGNORECASE)


message_test = on_command("test_message")
download = on_command("download", permission=SUPERUSER, priority=1)


@message_test.handle()
async def test_handler():
    test_dto = await Formatter.json2dto(f'{os.getcwd()}/src/plugins/star_relive/util/sample.json')
    test_simple = await Formatter.dto2dict(test_dto)
    await message_test.finish(str(test_simple))


@download.handle()
async def download_handler(matcher: Matcher, args: Message = CommandArg()):
    force_rewrite = args.extract_plain_text()
    if not force_rewrite:
        updated_entries = await batch_download()
        await download.finish(f"Updated {updated_entries} records.")
        # await download.finish("Fake update finished.")
    else:
        if force_rewrite != "rewrite":
            await download.finish(f"Invalid argument '{force_rewrite}'")
        else:
            await download.pause("Confirm force-rewriting current data?")

@download.handle()
async def _(args: Message = EventMessage()):
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
            # await download.finish("Fake update finished.")