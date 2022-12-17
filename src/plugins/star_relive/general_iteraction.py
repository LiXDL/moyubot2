from nonebot import on_keyword, get_driver
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


speak_test = on_keyword({"说话"}, rule=to_me())


@speak_test.handle()
async def speak_test_handle(event: GroupMessageEvent):
    await speak_test.finish(MessageSegment.image(plugin_config.other_image / "sneaking.png"))