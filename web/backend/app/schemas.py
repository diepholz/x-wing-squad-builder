from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be 3–50 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


# ── Squads ────────────────────────────────────────────────────────────────────

class SquadCreate(BaseModel):
    name: str
    faction: str
    data: Any  # SquadData JSON object


class SquadUpdate(BaseModel):
    name: Optional[str] = None
    faction: Optional[str] = None
    data: Optional[Any] = None


class SquadResponse(BaseModel):
    id: int
    name: str
    faction: str
    data: Any
    share_token: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime


class ShareResponse(BaseModel):
    share_token: str
    share_url: str


class SharedSquadResponse(BaseModel):
    squad: SquadResponse
    owner: str
