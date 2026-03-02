import json
import secrets
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from ..models import Squad, User
from ..auth import require_user, get_current_user
from ..schemas import SquadCreate, SquadUpdate, SquadResponse, ShareResponse, SharedSquadResponse

router = APIRouter()


def _squad_to_response(squad: Squad) -> SquadResponse:
    return SquadResponse(
        id=squad.id,
        name=squad.name,
        faction=squad.faction,
        data=json.loads(squad.data),
        share_token=squad.share_token,
        owner_id=squad.owner_id,
        created_at=squad.created_at,
        updated_at=squad.updated_at,
    )


@router.get("", response_model=list[SquadResponse])
async def list_squads(
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.owner_id == user.id))
    return [_squad_to_response(s) for s in result.all()]


@router.post("", response_model=SquadResponse, status_code=201)
async def create_squad(
    body: SquadCreate,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    squad = Squad(
        name=body.name,
        faction=body.faction,
        data=json.dumps(body.data),
        owner_id=user.id,
    )
    session.add(squad)
    await session.commit()
    await session.refresh(squad)
    return _squad_to_response(squad)


@router.get("/{squad_id}", response_model=SquadResponse)
async def get_squad(
    squad_id: int,
    user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.id == squad_id))
    squad = result.first()
    if not squad:
        raise HTTPException(404, "Squad not found")
    # Public if shared, otherwise must be owner
    if squad.owner_id != (user.id if user else None) and not squad.share_token:
        raise HTTPException(403, "Forbidden")
    return _squad_to_response(squad)


@router.put("/{squad_id}", response_model=SquadResponse)
async def update_squad(
    squad_id: int,
    body: SquadUpdate,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.id == squad_id))
    squad = result.first()
    if not squad:
        raise HTTPException(404, "Squad not found")
    if squad.owner_id != user.id:
        raise HTTPException(403, "Forbidden")

    if body.name is not None:
        squad.name = body.name
    if body.faction is not None:
        squad.faction = body.faction
    if body.data is not None:
        squad.data = json.dumps(body.data)
    squad.updated_at = datetime.utcnow()

    session.add(squad)
    await session.commit()
    await session.refresh(squad)
    return _squad_to_response(squad)


@router.delete("/{squad_id}")
async def delete_squad(
    squad_id: int,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.id == squad_id))
    squad = result.first()
    if not squad:
        raise HTTPException(404, "Squad not found")
    if squad.owner_id != user.id:
        raise HTTPException(403, "Forbidden")
    await session.delete(squad)
    await session.commit()
    return {"ok": True}


@router.post("/{squad_id}/share", response_model=ShareResponse)
async def share_squad(
    squad_id: int,
    request: Request,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.id == squad_id))
    squad = result.first()
    if not squad:
        raise HTTPException(404, "Squad not found")
    if squad.owner_id != user.id:
        raise HTTPException(403, "Forbidden")

    if not squad.share_token:
        squad.share_token = secrets.token_urlsafe(16)
        session.add(squad)
        await session.commit()
        await session.refresh(squad)

    base = str(request.base_url).rstrip("/")
    return ShareResponse(
        share_token=squad.share_token,
        share_url=f"{base}/share/{squad.share_token}",
    )


@router.get("/share/{share_token}", response_model=SharedSquadResponse)
async def view_shared(
    share_token: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Squad).where(Squad.share_token == share_token))
    squad = result.first()
    if not squad:
        raise HTTPException(404, "Not found")

    owner_result = await session.exec(select(User).where(User.id == squad.owner_id))
    owner = owner_result.first()

    return SharedSquadResponse(squad=_squad_to_response(squad), owner=owner.username)
