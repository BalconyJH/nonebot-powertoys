from nonebot import get_driver
from pydantic import BaseModel


class ProgressBarConfig(BaseModel):
    private: bool = False
    group:bool = False


class Config(BaseModel):
    progressbar: ProgressBarConfig


plugin_config = Config.parse_obj(get_driver().config)
# plugin_config = get_plugin_config(Config)
