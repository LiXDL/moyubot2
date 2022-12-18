import random

from nonebot import on_keyword, get_driver
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


speak_test = on_keyword({"zaima", "说话"}, rule=to_me(), priority=20)
gnssw = on_keyword({"色图", "涩图"}, priority=20)


gn_img_list = ["baal_gnssw.jpg", "nnami_gnzs.jpg", "scarlet_gn.jpg"]


@speak_test.handle()
async def speak_test_handle(event: GroupMessageEvent):
    await speak_test.finish(MessageSegment.image(plugin_config.other_image / "sneaking.jpg"))


@gnssw.handle()
async def gnssw_handle(event: GroupMessageEvent):
    send_flag = random.random()
    if send_flag >= 0.2:
        await gnssw.finish()
    else:
        gn_img = random.choice(gn_img_list)
        await gnssw.finish(MessageSegment.image(plugin_config.other_image / gn_img))