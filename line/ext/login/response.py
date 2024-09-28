from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str = Field(alias="userId")
    display_name: str = Field(alias="displayName")
    picture_url: str = Field(None, alias="pictureUrl")
    status_message: str = Field(None, alias="statusMessage")
