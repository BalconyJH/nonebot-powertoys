import datetime

from nonebot import on_command
import nonebot_plugin_saa as saa
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="年进度条",
    description="表示当前年份进度",
    type="application",
    usage="""
    [年进度]
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
)

year_progress = on_command("年进度", priority=5, block=True)


def generate_progress_bar(length: int = 20):
    """
    生成年进度条
    :param length: 进度条长度
    :return: 进度条字符串
    """
    current_year = datetime.datetime.now().year
    current_day = datetime.datetime.now().timetuple().tm_yday

    if current_year % 400 == 0 or (current_year % 100 != 0 and current_year % 4 == 0):
        total_days = 366
    else:
        total_days = 365

    percentage = current_day * 100 // total_days

    filled_length = length * percentage // 100
    bar = "▓" * filled_length + "░" * (length - filled_length)

    return f"{bar} {percentage}%"


@year_progress.handle()
async def _():
    progress_str = generate_progress_bar()
    msg_builder = saa.MessageFactory([saa.Text(progress_str)])
    await msg_builder.finish()


year_length = (
    366
    if datetime.datetime.now().year % 4 == 0
    and (datetime.datetime.now().year % 100 != 0 or datetime.datetime.now().year % 400 == 0)
    else 365
)
update_interval_hours = round((year_length / 100) * 24)

# @scheduler.scheduled_job("interval", hour=update_interval_hours, id="progress_bar_schedules_tasks")
# async def progress_bar_schedules_tasks():
#     if plugin_config.progressbar.private:
#         user_list = await OBV11Bot().get_friend_list()
