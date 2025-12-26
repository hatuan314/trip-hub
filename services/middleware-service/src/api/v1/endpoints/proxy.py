import httpx
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from src.api.v1.dependencies import get_current_user


from src.config.settings import settings
from src.core.bootstrap import service_router


router = APIRouter()

ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


@router.api_route("/{service}", methods=ALLOWED_METHODS)
async def proxy_root(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.api_route("/{service}/{path:path}", methods=ALLOWED_METHODS)
async def proxy_request(
    service: str, request: Request, path: str = "", user=Depends(get_current_user)
):
    target_url = service_router.build_target(service_name=service, path=path)
    if not target_url:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service}'")

    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                params=request.query_params,
                headers=headers,
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504, detail=f"Request to {service} timed out"
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"Error forwarding request to {service}"
        ) from exc

    filtered_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower()
        not in {"content-length", "transfer-encoding", "connection", "content-encoding"}
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=filtered_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
