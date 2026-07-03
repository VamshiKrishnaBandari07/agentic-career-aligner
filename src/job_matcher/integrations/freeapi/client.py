import httpx

from job_matcher.core.config import Settings


class FreeAPIClient:
    """Client for hiteshchoudhary/apihub public endpoints (https://api.freeapi.app)."""

    def __init__(self, settings: Settings) -> None:
        self._base = settings.freeapi_base_url.rstrip("/")
        self._timeout = settings.freeapi_timeout

    async def healthcheck(self) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(f"{self._base}/healthcheck")
            response.raise_for_status()
            return response.json()

    async def random_quote(self) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(f"{self._base}/public/quotes/quote/random")
            response.raise_for_status()
            payload = response.json()
            return payload.get("data", payload)
