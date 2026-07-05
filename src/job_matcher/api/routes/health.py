from fastapi import APIRouter, Depends

from job_matcher.api.deps import get_settings
from job_matcher.core.config import Settings
from job_matcher.core.schemas.match import HealthResponse
from job_matcher.integrations.freeapi.client import FreeAPIClient

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        openai_configured=settings.openai_configured,
        match_provider=settings.match_provider,
        free_mode=settings.uses_free_local or not settings.openai_configured,
        serve_ui=settings.serve_ui,
        ready=True,
    )


@router.get("/freeapi/status")
async def freeapi_status(settings: Settings = Depends(get_settings)) -> dict:
    client = FreeAPIClient(settings)
    try:
        data = await client.healthcheck()
        return {"status": "ok", "freeapi": data, "docs": "https://api.freeapi.app"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc), "docs": "https://api.freeapi.app"}
