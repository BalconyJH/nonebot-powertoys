from typing import Optional

from pydantic import BaseModel, Field


class LoginInfo(BaseModel):
    username: str = Field(..., title="Username")
    password: str = Field(..., title="Password")
    nn_token: str = Field(..., title="NN Token")
    access_token: str = Field(..., title="Access Token")
    expiry_time: int = Field(..., title="Token expiration time in seconds")

    class Config:
        extra = "ignore"


class IPInfo(BaseModel):
    last_login_ip: str = Field(..., title="IP Address of last login")
    last_login_time: str = Field(..., title="TimeStamp of last login")
    public_ip: str = Field(..., title="Public IP Address")

    class Config:
        extra = "ignore"


class TimerInfo(BaseModel):
    pause_status_id: int = Field(..., title="Pause status ID, 1 for paused, 0 for in used")
    user_earn_minutes: int = Field(..., title="User's earned minutes")
    expiry_time_samp: int = Field(..., title="TimeStamp of expiry time")
    expiry_time: str = Field(..., title="Expiry time")
    last_pause_time: str = Field(..., title="Last pause time")

    class Config:
        extra = "ignore"


class UserInfo(BaseModel):
    avatar: str = Field(..., title="Avatar URL")
    mobile: Optional[str] = Field(None, title="Phone number")
    email: Optional[str] = Field(None, title="Email address")
    nickname: str = Field(..., title="Nickname")
    region_code: str = Field(..., title="Region code")

    class Config:
        extra = "ignore"


class User(BaseModel):
    login_info: Optional[LoginInfo] = Field(None, title="Login information")
    user_info: Optional[UserInfo] = Field(None, title="User information")
    timer_info: Optional[TimerInfo] = Field(None, title="Timer information")
    ip_info: Optional[IPInfo] = Field(None, title="IP information")

    class Config:
        extra = "ignore"


async def parse_user_info(data: dict) -> User:
    return User(user_info=UserInfo(**data), timer_info=TimerInfo(**data))  # type: ignore
