import json
import contextlib
from typing import Union, Callable, Optional

from nonebot.internal.params import Depends
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message as V11Message
from nonebot.adapters.onebot.v12 import Message as V12Message
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12 import MessageEvent as V12MessageEvent


async def _match(
    matcher: Matcher,
    event: V11MessageEvent,
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


def get_message_img(data: Union[str, Union[V11Message, V12Message]]) -> list[str]:
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
                    img_list.append(msg["data"]["file"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["file"])
    return img_list


def image_list(msg: Optional[str] = None, contain_reply: bool = True) -> list[str]:
    """
    说明:
        获取图片列表（包括回复时），含有msg时不能为空，为空时提示并结束事件
        only for Onebotv11
    参数:
        :param msg: 提示文本
        :param contain_reply: 包含回复内容
    """

    async def dependency(matcher: Matcher, event: V11MessageEvent):
        return await _match(matcher, event, msg, get_message_img, contain_reply)

    return Depends(dependency)


def is_number(s: Union[int, str]) -> bool:
    """
    说明:
        检测 s 是否为数字
    参数:
        :param s: 文本
    """
    if isinstance(s, int):
        return True
    with contextlib.suppress(ValueError):
        float(s)
        return True
    with contextlib.suppress(TypeError, ValueError):
        import unicodedata

        unicodedata.numeric(s)
        return True
    return False
