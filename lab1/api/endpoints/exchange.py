from fastapi import APIRouter, Depends

from api.models.connection import get_session
from api.schemas.exchange_schemas import ExchangeResponse


router_exchange = APIRouter()



@router_exchange.get("/exchange_get")
def exchanges_get():
    pass

@router_exchange.post("/exchange_create")
def exchange_create(exchange: ExchangeResponse, session=Depends(get_session)):
    pass
