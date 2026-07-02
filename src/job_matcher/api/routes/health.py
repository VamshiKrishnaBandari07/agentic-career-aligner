from fastapi import APIRouter, Depends

from job_matcher.api.deps import get_settings
from job_matcher.core.config import Settings
from job_matcher.core.schemas.match import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(openai_configured=settings.openai_configured)
