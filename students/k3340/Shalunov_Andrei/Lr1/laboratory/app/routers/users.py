from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

import app.schemas as schemas
import app.crud as crud
from app.database import get_session
from app.routers.auth import authenticate_request

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(authenticate_request)],
)


@router.get("/me", response_model=schemas.ProfileRead)
def read_me(current: schemas.ProfileRead = Depends(authenticate_request)):
    return current


@router.get("/", response_model=List[schemas.ProfileRead])
def list_profiles(db: Session = Depends(get_session)):
    return crud.get_profiles(db)


@router.get("/{profile_id}", response_model=schemas.ProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_session)):
    prof = crud.get_profile(db, profile_id)
    if not prof:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return prof


@router.patch("/me", response_model=schemas.ProfileRead)
def patch_me(
    patch: schemas.ProfilePatch,
    current: schemas.ProfileRead = Depends(authenticate_request),
    db: Session = Depends(get_session),
):
    return crud.update_profile(db, current.id, patch)


@router.patch("/change-password")
def change_password(
    pw: schemas.PasswordChange,
    current: schemas.ProfileRead = Depends(authenticate_request),
    db: Session = Depends(get_session),
):
    try:
        crud.change_password(db, current, pw.old_password, pw.new_password)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return {"msg": "Password updated"}