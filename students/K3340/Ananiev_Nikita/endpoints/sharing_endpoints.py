from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from models.models import ShareRequest, ShareRequestDefault
from models.public_models import ShareRequestPatch
from connection import get_session
from helpers import upd_model, get_object_by_id
from .auth_endpoints import auth_checker
from jwt_logic import bearer_scheme
from typing_extensions import TypedDict

share_router = APIRouter()

@share_router.post('/share_request')
@auth_checker
async def create_sharing_request(new_request: ShareRequestDefault,
                           credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                           session=Depends(get_session)) -> TypedDict('Response', {"status": int, "created": ShareRequest}):
    new_request = ShareRequest.model_validate(new_request)
    session.add(new_request)
    session.commit()
    session.refresh(new_request)
    return {"status": 201, "created": new_request}


@share_router.get('/share_request/{id}', response_model=ShareRequest)
@auth_checker
async def get_share_request(req_id: int, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme), session=Depends(get_session)):
    return get_object_by_id(req_id, ShareRequest, session)


@share_router.patch('/share_request/{id}')
@auth_checker
async def update_share_request(req_id: int, upd_request: ShareRequestPatch,
                               credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                               session=Depends(get_session)) -> TypedDict('Response', {"status": int, "updated": ShareRequest}):
    req = get_object_by_id(req_id, ShareRequest, session)
    upd_data = upd_request.model_dump(exclude_unset=True)
    req = upd_model(req, upd_data, session)
    return {"status": 202, "updated": req}
