import httpx

AUTH_CORE_URL = "http://localhost:8000/api/v1/auth"


async def sync_register(username: str, password: str):
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(
            f"{AUTH_CORE_URL}/register",
            json={"username": username, "password": password},
        )

        # 409 / 400 -> user đã tồn tại bên 8000 thì coi là OK
        if resp.status_code in (400, 409):
            return {"message": "already synced"}

        resp.raise_for_status()
        return resp.json()
