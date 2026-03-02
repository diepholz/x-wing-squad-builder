from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(index=True, unique=True, max_length=254)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    squads: List["Squad"] = Relationship(back_populates="owner")


class Squad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    faction: str = Field(max_length=100)
    # SquadData stored as a JSON string
    data: str = Field(default="{}")
    share_token: Optional[str] = Field(default=None, index=True)
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="squads")
