import random

from nonebot import on_keyword, on_fullmatch, get_driver
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(driver.config)


general_help = on_fullmatch("帮助", rule=to_me(), priority=20)
speak = on_keyword({"zaima", "说话"}, rule=to_me(), priority=20)
gnssw = on_keyword({"色图", "涩图", "瑟图"}, priority=20)


general_help_message = """
亲爱的长颈鹿你好，我是你蝶

目前为本群提供以下功能：
0.歌卫兵开发的查卡器，可使用【/查卡 -h】或【/常用名 -h】查看详细帮助信息
1.小刘同学提供的每日占卜功能，发送【小刘抽签】即可使用
2.星见同学提供的每日名人名言
3.神必小功能

TODO：
0.不要想有搜图功能，容易炸号
1.不知道
""".strip()
gn_img_list = ["baal_gnssw.jpg", "nanami_gnzs.jpg", "scarlet_gn.jpg"]


@general_help.handle()
async def general_help_handle():
    await general_help.finish(general_help_message)


@speak.handle()
async def speak_handle(event: GroupMessageEvent):
    await speak.finish(MessageSegment.image(plugin_config.other_image / "sneaking.jpg"))


@gnssw.handle()
async def gnssw_handle(event: GroupMessageEvent):
    send_flag = random.random()
    if send_flag >= 0.5:
        await gnssw.finish()
    else:
        gn_img = random.choice(gn_img_list)
        await gnssw.finish(MessageSegment.image(plugin_config.other_image / gn_img))