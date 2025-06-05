import uuid
import os
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator

from ...models import User, Player
from ...config import save_upload_file, PLAYER_PHOTOS_DIR, PLAYER_CERTIFICATES_DIR
from ...config import ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES
from ..users.user_security import get_current_active_user, get_session
from ..players.crud import get_user_with_roles

router = APIRouter(prefix="/documents", tags=["player documents"])


class SnilsUpdate(BaseModel):
    snils: str = Field(..., description="SNILS number (11 digits)")

    @validator('snils')
    def validate_snils(cls, v):
        # Convert to string if it's a number
        if isinstance(v, int):
            v = str(v)

        v = ''.join(filter(str.isdigit, v))

        if len(v) != 11:
            raise ValueError('SNILS must be exactly 11 digits')
        return v

async def get_player_by_id(player_id: int, session: AsyncSession):
    result = await session.execute(
        select(Player).where(Player.player_id == player_id).options(selectinload(Player.team))
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with ID {player_id} not found")
    return player


async def check_player_permission(player: Player, user: User, session: AsyncSession, require_team_owner=True):
    user_with_roles = await get_user_with_roles(user.user_id, session)
    is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)

    is_team_owner = player.team.user_id == user.user_id if player.team else False

    if (require_team_owner and not is_team_owner) and not is_admin:
        raise HTTPException(status_code=403, detail="Отказано в доступе")

    return is_admin or is_team_owner


@router.post("/photo/{player_id}")
async def upload_player_photo(
        player_id: int,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player, current_user, session)

    photo_url = await save_upload_file(file, PLAYER_PHOTOS_DIR, ALLOWED_IMAGE_TYPES)
    player.photo_url = photo_url
    await session.commit()
    return {"photo_url": photo_url}


@router.post("/snils/{player_id}")
async def update_player_snils(
        player_id: int,
        snils_data: SnilsUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player, current_user, session, require_team_owner=True)

    player.snils = snils_data.snils
    await session.commit()
    return {"snils": player.snils}


@router.post("/birth-certificate/{player_id}")
async def upload_birth_certificate(
        player_id: int,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player, current_user, session, require_team_owner=True)

    document_uuid = str(uuid.uuid4())
    cert_url = await save_upload_file(file, PLAYER_CERTIFICATES_DIR, ALLOWED_DOCUMENT_TYPES + ALLOWED_IMAGE_TYPES,
                                      filename=document_uuid)
    player.birth_certificate = cert_url
    await session.commit()
    return {"birth_certificate": cert_url, "document_uuid": document_uuid}


@router.patch("/consent/{player_id}")
async def update_player_consent(
        player_id: int,
        consent: bool = Form(...),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player,   current_user, session, require_team_owner=True)

    player.consent = consent
    await session.commit()
    return {"consent": consent}


@router.get("/photo/{player_id}")
async def get_player_photo(
        player_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)

    if not player.photo_url or not os.path.exists(player.photo_url):
        raise HTTPException(status_code=404, detail="Фото не найдено")

    return FileResponse(
        player.photo_url,
        media_type="image/png",
        filename=f"player_{player_id}_photo.png"
    )


@router.get("/snils/{player_id}")
async def get_player_snils(
        player_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player, current_user, session, require_team_owner=True)

    if not player.snils:
        raise HTTPException(status_code=404, detail="СНИЛС не найден")

    return {"snils": player.snils}


@router.get("/birth-certificate/{player_id}")
async def get_player_birth_certificate(
        player_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player_by_id(player_id, session)
    await check_player_permission(player, current_user, session, require_team_owner=True)

    if not player.birth_certificate or not os.path.exists(player.birth_certificate):
        raise HTTPException(status_code=404, detail="Свидетельство рождения не найдено")

    _, file_ext = os.path.splitext(player.birth_certificate)
    file_ext = file_ext.lower()

    if file_ext == '.pdf':
        content_type = "application/pdf"
    elif file_ext == '.png':
        content_type = "image/png"
    elif file_ext in ['.jpg', '.jpeg']:
        content_type = "image/jpeg"
    else:
        content_type = "application/octet-stream"

    return FileResponse(
        player.birth_certificate,
        media_type=content_type,
        filename=f"player_{player_id}_birth_certificate{file_ext}"
    )


@router.get("/secure/{document_uuid}")
async def get_secure_document(
        document_uuid: str,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    user_with_roles = await get_user_with_roles(current_user.user_id, session)
    is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)

    result = await session.execute(
        select(Player).where(
            (Player.birth_certificate.contains(document_uuid))
        ).options(selectinload(Player.team))
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Документ не найден")

    if not is_admin and (player.team and player.team.user_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Отказано в доступе")

    file_path = None
    if player.birth_certificate and document_uuid in player.birth_certificate:
        file_path = player.birth_certificate

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Документ не найден")

    _, file_ext = os.path.splitext(file_path)
    file_ext = file_ext.lower()

    if file_ext == '.pdf':
        content_type = "application/pdf"
    elif file_ext == '.png':
        content_type = "image/png"
    elif file_ext in ['.jpg', '.jpeg']:
        content_type = "image/jpeg"
    else:
        content_type = "application/octet-stream"

    return FileResponse(
        file_path,
        media_type=content_type,
        filename=f"document_{document_uuid}{file_ext}"
    )