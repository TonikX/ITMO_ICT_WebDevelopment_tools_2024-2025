from fastapi import APIRouter, Request, Response
import httpx
from config.secrets import PARSER_URL

router = APIRouter(tags=["Parse"], prefix="/parse")


@router.post("/")
async def proxy_parse(
    request: Request,
    pages_to_parse: int = 1,
):
    async with httpx.AsyncClient(timeout=None) as client:
        body = await request.body()
        headers = dict(request.headers)
        resp = await client.post(
            PARSER_URL,
            content=body,
            headers=headers,
            params={"pages_to_parse": pages_to_parse},
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)


@router.post("/async")
async def proxy_parse_async(
    request: Request,
    pages_to_parse: int = 1,
):
    async with httpx.AsyncClient(timeout=None) as client:
        body = await request.body()
        headers = dict(request.headers)
        resp = await client.post(
            f"{PARSER_URL}/async",
            content=body,
            headers=headers,
            params={"pages_to_parse": pages_to_parse},
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)


@router.get("/async/status/{task_id}")
async def get_task_status():
    async with httpx.AsyncClient(timeout=None) as client:
        task_id = httpx.request.path_params.get("task_id")
        resp = await client.get(f"{PARSER_URL}/async/status/{task_id}")
        return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
