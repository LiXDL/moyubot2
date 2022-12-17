from nonebot import on_keyword
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent


speak_test = on_keyword({"说话"}, rule=to_me())


@speak_test.handle()
async def speak_test_handle(event: GroupMessageEvent):
    await speak_test.finish("")