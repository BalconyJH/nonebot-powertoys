import asyncio
import json
from typing import List
from typing import Union, Optional, Callable

import nonebot_plugin_saa as saa
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot as V11Bot, MessageEvent as V11MessageEvent, Message as V11Message
from nonebot.adapters.onebot.v12 import Bot as V12Bot, MessageEvent as V12MessageEvent, Message as V12Message
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import Depends
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from nonebot_plugin_saa import enable_auto_select_bot
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


async def _match(
        matcher: Matcher,
        event: Union[V11MessageEvent, V12MessageEvent],
        msg: Optional[str],
        func: Callable,
        contain_reply: bool,
):
    _list = func(event.message)
    if event.reply and contain_reply:
        _list = func(event.reply.message)
    if not _list and msg:
        await matcher.finish(msg)
    return _list


def get_message_text(data: Union[str, Union[V11Message, V12Message]]) -> str:
    """
    说明:
        获取消息中 纯文本 的信息
    参数:
        :param data: event.json()
    """
    result = ""
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            if isinstance(message, str):
                return message.strip()
            for msg in message:
                if msg["type"] == "text":
                    result += msg["data"]["text"].strip() + " "
        return result.strip()
    else:
        for seg in data["text"]:
            result += seg.data["text"] + " "
    return result.strip()


def get_message_img(data: Union[str, Union[V11Message, V12Message]]) -> List[str]:
    """
    说明:
        获取消息中所有的 图片 的链接
    参数:
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            for msg in message:
                if msg["type"] == "image":
                    img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list


def image_list(msg: Optional[str] = None, contain_reply: bool = True) -> List[str]:
    """
    说明:
        获取图片列表（包括回复时），含有msg时不能为空，为空时提示并结束事件
    参数:
        :param msg: 提示文本
        :param contain_reply: 包含回复内容
    """

    async def dependency(matcher: Matcher, event: Union[V11MessageEvent, V12MessageEvent]):
        return await _match(matcher, event, msg, get_message_img, contain_reply)

    return Depends(dependency)


@broadcast.handle()
async def _(
        bot: Union[V11Bot, V12Bot],
        event: Union[V11MessageEvent, V12MessageEvent],
        arg: Union[V11Message, V12Message] = CommandArg(),
):
    msg = arg.extract_plain_text().strip()
    rst = ""
    img_list = get_message_img(arg)
    for img in img_list:
        rst += saa.Image(img)
    print(await bot.get_group_list())
    gl = [
        g["group_id"]
        for g in await bot.get_group_list()
    ]
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
            msg_builder = saa.MessageFactory([saa.Text(msg)])
            await msg_builder.send_to(target, bot=bot)
            logger.info("投递广播成功", "广播", group_id=g)
        except Exception as e:
            logger.error("投递广播失败", "广播", group_id=g, e=e)
            error += f"GROUP {g} 投递广播失败：{e}\n"
        await asyncio.sleep(0.5)
    await broadcast.send("已播报至 100% 的群聊")
    if error:
        await broadcast.send(f"播报时错误：{error}")


@test.handle()
async def _(bot: Union[V11Bot, V12Bot],
            event: Union[V11MessageEvent, V12MessageEvent],
            arg: Union[V11Message, V12Message] = CommandArg(), ):
    msg_builder = saa.Text("test")
    await msg_builder.finish()
