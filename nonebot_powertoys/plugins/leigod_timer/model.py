from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    mobile: str = Field(..., title="Phone number")
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
    account_info: ContactInfo
    timer_info: TimerInfo

    class Config:
        extra = "ignore"


async def parse_user_info(data: dict) -> UserInfo:
    return UserInfo(account_info=ContactInfo(**data), timer_info=TimerInfo(**data))
