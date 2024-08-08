import json
from typing import Union, Optional

from nonebot import on_command
import nonebot_plugin_saa as saa
import nonebot_plugin_localstore as store
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12 import MessageEvent as V12MessageEvent

from .utils import Leigod

__plugin_meta__ = PluginMetadata(
    name="加速器暂停",
    description="雷神加速器暂停",
    type="application",
    usage="""
    [雷神暂停]
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
)

leigod_timer_login = on_command("雷神登录", priority=5, block=True)
leigod_timer_logout = on_command("雷神登出", priority=5, block=True)
leigod_timer = on_command("雷神剩余时长", priority=5, block=True)
leigod_timer_pause = on_command("雷神暂停", priority=5, block=True)
cache_path = store.get_data_dir("nonebot_powertoys") / "leigod_timer" / "user_info.json"


async def load_user_info() -> Optional[dict]:
    try:
        return await json.load(cache_path.open())
    except FileNotFoundError:
        return None


@leigod_timer_login.handle()
async def _(
    event: Union[V11MessageEvent, V12MessageEvent],
):
    data = await load_user_info()
    if data is not None:
        login_status = await Leigod.login_status(str(event.user_id), data)
        msg_builder = saa.MessageFactory([saa.Text("已暂停")])
        await msg_builder.finish()
