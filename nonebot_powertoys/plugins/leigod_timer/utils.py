import json
import hashlib
from typing import Optional

import httpx
from nonebot import logger

from nonebot_powertoys.plugins.leigod_timer.model import User, IPInfo, UserInfo, LoginInfo, TimerInfo


class Leigod:
    def __init__(self):
        self.info_url = "https://webapi.leigod.com/api/user/info"
        self.login_url = "https://webapi.leigod.com/api/auth/login"
        self.pauser_url = "https://webapi.leigod.com/api/auth/pause"
        self.header = {
            # ':authority': 'webapi.nn.com',
            # ':method':'POST',
            # ':path':'/api/user/pause',
            # ':scheme': 'https',
            # "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
            # Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53",
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Connection":"keep-alive",
            # "Accept": "application/json, text/javascript, */*; q=0.01",
            # "Accept-Encoding": "gzip, deflate, br",
            # "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            # "DNT": "1",
            # "Referer": "https://www.legod.com/",
            # "Sec-Fetch-Dest": "empty",
            # "Sec-Fetch-Mode": "cors",
            # "Sec-Fetch-Site": "same-site"
        }  # 好像不需要(?)

    @staticmethod
    def _md5_string(string: str):
        md5 = hashlib.md5()
        md5.update(string.encode(encoding="utf-8"))
        return md5.hexdigest()

    async def login(self, username: str, password: str) -> Optional[User]:
        body = {
            "username": username,
            "password": self._md5_string(password),
            "user_type": "0",
            "src_channel": "guanwang",
            "country_code": 86,
            "lang": "zh_CN",
            "region_code": 1,
            "account_token": "null",
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.login_url, json=body)
                response.raise_for_status()
                json_response = response.json()

                if json_response["code"] == 0:
                    login_info = LoginInfo(
                        username=username,
                        password=password,
                        **json_response["data"]["login_info"],
                    )
                    user_info = UserInfo(**json_response["data"]["user_info"])
                    return User(login_info=login_info, user_info=user_info)  # type: ignore
                else:
                    return None
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTPStatusError: {e}")
                return None
            except httpx.RequestError as e:
                logger.error(f"RequestError: {e}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e}")
                return None

    async def get_user_info(self, access_token: str) -> Optional[User]:
        """
        Asynchronously get user info from Leigod using the provided access token.
        :param access_token: The access token for authentication.
        :return: dict if successful, None if an error occurs or if the token is invalid.
        """
        payload = {
            "access_token": access_token,
            "lang": "zh_CN",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.info_url, params=payload, headers=self.header)
                response.raise_for_status()
                json_response = response.json()

                if json_response["code"] == 0:
                    return User(
                        timer_info=TimerInfo(**json_response["data"]),
                        ip_info=IPInfo(**json_response["data"]),
                    )  # type: ignore
                elif json_response["code"] == 400006:
                    logger.error("Token is invalid or has expired.")
                    return None
                else:
                    logger.error(f"Error code from API: {json_response.get('msg', 'Unknown error')}")
                    return None
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                logger.error(f"HTTP error occurred: {e}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON response: {e}")
                return None

    async def timer_status(self, token: str) -> bool:
        """
        Check if the user has paused the timer.
        :return: True if the timer is paused, False otherwise.
        """
        user_info = await self.get_user_info(token)
        return user_info is not None and user_info.timer_info is not None and user_info.timer_info.pause_status_id == 1

    async def pause_timer(self, access_token: str):
        """
        Pause the timer.
        :param: access_token： The access token for authentication.
        :return: True if successful, False otherwise.
        """
        if await self.timer_status(access_token):
            return True
        else:
            body = {
                "account_token": access_token,
                "lang": "zh_CN",
            }
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(self.pauser_url, data=body, headers=self.header)
                    response.raise_for_status()
                    json_response = response.json()

                    if json_response["code"] == 0:
                        return True
                    elif json_response["code"] == 400006:
                        logger.error("Token is invalid or has expired.")
                        return False
                    else:
                        logger.error(f"Error code from API: {json_response.get('code', 'Unknown error')}")
                        return False
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logger.error(f"HTTP error occurred: {e}")
                    return False
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON response: {e}")
                    return False

    @staticmethod
    async def login_status(uid: str, data: dict) -> bool:
        user = data.get(uid)
        if user is None:
            return False
        return True

    @staticmethod
    async def time_remaining(user_info: TimerInfo) -> int:
        """
        Get the remaining time in seconds.
        :param user_info: The user info dict.
        :return: The remaining time in seconds.
        """
        return user_info.expiry_time_samp
