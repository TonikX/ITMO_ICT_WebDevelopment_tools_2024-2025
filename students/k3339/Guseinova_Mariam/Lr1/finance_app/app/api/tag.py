from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.tag import create_tag, get_tags, add_tag_to_transaction, remove_tag_from_transaction, get_tag, update_tag, delete_tag
from app.schemas.tag import TagCreate, TagOut, TransactionTagCreate, TagUpdate
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user
from app.models.user import User
from app.models.transaction import Transaction


router = APIRouter(tags=["Tags"])


@router.post("/tags", response_model=TagOut)
def create_new_tag(
        tag: TagCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        return create_tag(db, tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tags", response_model=list[TagOut])
def get_all_tags(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    return get_tags(db, skip=skip, limit=limit)


@router.get("/tags/{tag_id}", response_model=TagOut)
def get_single_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.put("/tags/{tag_id}", response_model=TagOut)
def update_tag_endpoint(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated = update_tag(db, tag_id, tag_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Tag not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tags/{tag_id}")
def delete_tag_endpoint(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"msg": "Tag deleted"}


@router.post("/transactions/{transaction_id}/tags")
def add_tag(
        transaction_id: int,
        tag_id: int,
        tag_data: TransactionTagCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction or transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return add_tag_to_transaction(db, transaction_id, tag_id, tag_data.context)


@router.delete("/transactions/{transaction_id}/tags/{tag_id}")
def remove_tag(
        transaction_id: int,
        tag_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction or transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    success = remove_tag_from_transaction(db, transaction_id, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not linked to transaction")
    return {"msg": "Tag removed"}