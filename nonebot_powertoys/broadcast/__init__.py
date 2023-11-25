import asyncio

import nonebot_plugin_saa as saa
from nonebot import logger, on_command
from nonebot.adapters import Bot, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot_plugin_saa import enable_auto_select_bot

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
        bot: Bot,
        arg: Message = CommandArg(),
        img_list=None,
):
    if img_list is None:
        img_list = image_list()
    msg = arg.extract_plain_text().strip()
    rst = [saa.Image(img) for img in img_list]
    gl = [g["group_id"] for g in await bot.get_group_list()]

    async def send_broadcast(group_id, progress):
        try:
            target = saa.TargetQQGroup(group_id=group_id)
            msg_builder = saa.MessageFactory([saa.Text(msg), *rst])
            await msg_builder.send_to(target)
            logger.info("投递广播成功", "广播", group_id=group_id)
            if progress is not None:
                await broadcast.send(f"已播报至 {progress}% 的群聊")
            return None
        except Exception as e:
            logger.error("投递广播失败", "广播", group_id=group_id, e=e)
            return f"GROUP {group_id} 投递广播失败：{e}\n"
        finally:
            await asyncio.sleep(0.5)

    error = ""
    for cnt, g in enumerate(gl, start=1):
        _progress = int(cnt / len(gl) * 100)
        result = await send_broadcast(g, _progress if _progress % 25 == 0 or _progress == 100 else None)
        if result:
            error += result

    if error:
        await broadcast.send(f"播报时错误：{error}")


@test.handle()
async def handle_func():
    target_group = saa.TargetQQGroup(group_id=44781405)
    msg_builder = saa.MessageFactory([saa.Text("\n管理员回复\n"), saa.Mention(user_id=str(1066474894))])
    await msg_builder.send_to(target_group)
