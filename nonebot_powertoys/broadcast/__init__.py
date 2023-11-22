import asyncio
from typing import List, Union

import nonebot_plugin_saa as saa
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot_plugin_saa import enable_auto_select_bot
from nonebot.adapters.onebot.v11 import Message as V11Message
from nonebot.adapters.onebot.v12 import Message as V12Message
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12 import MessageEvent as V12MessageEvent

from nonebot_powertoys.utils import image_list

enable_auto_select_bot()
__plugin_meta__ = PluginMetadata(
    name="大喇叭",
    description="昭告天下！",
    type="application",
    usage="""
    [广播] 发送你想说的话
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
)

broadcast = on_command("广播", priority=1, permission=SUPERUSER, block=True)
test = on_command("test", priority=1, permission=SUPERUSER, block=True)


@broadcast.handle()
async def _(
    bot: Union[V11Bot, V12Bot],
    event: Union[V11MessageEvent, V12MessageEvent],
    arg: Union[V11Message, V12Message] = CommandArg(),
    img_list: List = image_list(),
):
    msg = arg.extract_plain_text().strip()
    rst = []
    for img in img_list:
        rst += saa.Image(img)
    gl = [g["group_id"] for g in await bot.get_group_list()]
    g_cnt = len(gl)
    cnt = 0
    error = ""
    x = 0.25
    for g in gl:
        cnt += 1
        if cnt / g_cnt > x:
            await broadcast.send(f"已播报至 {int(cnt / g_cnt * 100)}% 的群聊")
            x += 0.25
        try:
            target = saa.TargetQQGroup(group_id=g)
            msg_builder = saa.MessageFactory([saa.Text(msg), *rst])
            await msg_builder.send_to(target)
            logger.info("投递广播成功", "广播", group_id=g)
        except FileNotFoundError as e:
            logger.error("投递广播失败", "广播", group_id=g, e=e)
            error += f"GROUP {g} 投递广播失败：{e}\n"
        await asyncio.sleep(0.5)
    await broadcast.send("已播报至 100% 的群聊")
    if error:
        await broadcast.send(f"播报时错误：{error}")
