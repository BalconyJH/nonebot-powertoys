from nonebot import get_driver
from nonebot.plugin import PluginMetadata, require, inherit_supported_adapters

require("nonebot_plugin_saa")
require("nonebot_plugin_user")
require("nonebot_plugin_session")
require("nonebot_plugin_orm")

import nonebot_plugin_saa  # F401

nonebot_plugin_saa.enable_auto_select_bot()

__help__version__ = "0.1.0"
__help__plugin__name__ = "nonebot_powertoys"
__help__plugin__usage__ = """
    nonebot_powertoys.broadcast
    nonebot_powertoys.walkie_talkie
""".strip()
__plugin_meta__ = PluginMetadata(
    homepage="https://github.com/BalconyJH/nonebot-powertoys",
    name=__help__plugin__name__,
    description="nonebot_powertoys",
    usage=__help__plugin__usage__,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa", "nonebot_plugin_user"),
)

driver = get_driver()


@driver.on_startup
async def _():
    from nonebot_powertoys.plugins.broadcast import broadcast
    from nonebot_powertoys.plugins.walkie_talkie import reply, dialogue

    broadcast._plugin_meta = __plugin_meta__
    dialogue._plugin_meta = __plugin_meta__
    reply._plugin_meta = __plugin_meta__

    from .db.db_model import create_sqlite_database

    await create_sqlite_database()
