from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from job_matcher.api.routes import health, match
from job_matcher.core.exceptions import (
    ComparisonError,
    FileTooLargeError,
    JobMatcherError,
    OpenAINotConfiguredError,
    PDFParseError,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Job Matcher API",
        description="Parse PDF resumes and job descriptions, then semantically compare them with OpenAI.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(match.router)

    @app.exception_handler(PDFParseError)
    async def pdf_parse_handler(_: Request, exc: PDFParseError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(_: Request, exc: FileTooLargeError) -> JSONResponse:
        return JSONResponse(status_code=413, content={"detail": str(exc)})

    @app.exception_handler(OpenAINotConfiguredError)
    async def openai_not_configured_handler(
        _: Request, exc: OpenAINotConfiguredError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(ComparisonError)
    async def comparison_handler(_: Request, exc: ComparisonError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(JobMatcherError)
    async def domain_handler(_: Request, exc: JobMatcherError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "job_matcher.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
