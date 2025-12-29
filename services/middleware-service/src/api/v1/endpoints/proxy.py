from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from src.api.v1.dependencies import get_current_user


from src.config.settings import settings
from src.core.bootstrap import service_router


router = APIRouter()


@router.get("/{service}")
async def proxy_root_get(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.get("/{service}/{path:path}")
async def proxy_get(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


@router.post("/{service}")
async def proxy_root_post(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.post("/{service}/{path:path}")
async def proxy_post(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


@router.put("/{service}")
async def proxy_root_put(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.put("/{service}/{path:path}")
async def proxy_put(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


@router.patch("/{service}")
async def proxy_root_patch(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.patch("/{service}/{path:path}")
async def proxy_patch(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


@router.delete("/{service}")
async def proxy_root_delete(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.delete("/{service}/{path:path}")
async def proxy_delete(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


@router.options("/{service}")
async def proxy_root_options(service: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path="")


@router.options("/{service}/{path:path}")
async def proxy_options(service: str, request: Request, path: str = "", user=Depends(get_current_user)):
    return await proxy_request(service=service, request=request, path=path)


async def proxy_request(
    service: str, request: Request, path: str = ""
):
    # Build URL đích theo service map trong ServiceRouter.
    target_url = service_router.build_target(service_name=service, path=path)
    if not target_url:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service}'")

    base_url = service_router.get_base_url(service)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    body = await request.body()

    try:
        # Forward request giữ nguyên method/body/query/headers.
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
    if base_url and "location" in filtered_headers:
        parsed = urlparse(filtered_headers["location"])
        base_parsed = urlparse(base_url)
        is_same_host = (
            parsed.scheme == base_parsed.scheme and parsed.netloc == base_parsed.netloc
        )
        is_relative = not parsed.scheme and not parsed.netloc
        if is_same_host or is_relative:
            remainder = parsed.path or ""
            if parsed.query:
                remainder = f"{remainder}?{parsed.query}"
            if parsed.fragment:
                remainder = f"{remainder}#{parsed.fragment}"
            if remainder.startswith(settings.api_prefix):
                remainder = remainder[len(settings.api_prefix) :]
            if not remainder.startswith("/"):
                remainder = f"/{remainder}"
            filtered_headers["location"] = f"{settings.api_prefix}/{service}{remainder}"

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=filtered_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
