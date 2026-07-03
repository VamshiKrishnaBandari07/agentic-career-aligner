from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAIError
from starlette.exceptions import HTTPException as StarletteHTTPException

from job_matcher.api.routes import health, match
from job_matcher.core.exceptions import (
    ComparisonError,
    EmptyTextError,
    FileTooLargeError,
    JobMatcherError,
    OpenAINotConfiguredError,
    PDFParseError,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Career Aligner API",
        description="Upload resume and job description PDFs for semantic match analysis.",
        version="1.0.0",
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

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def home() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.exception_handler(EmptyTextError)
    async def empty_text_handler(_: Request, exc: EmptyTextError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

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

    @app.exception_handler(OpenAIError)
    async def openai_error_handler(_: Request, exc: OpenAIError) -> JSONResponse:
        from job_matcher.integrations.openai.errors import openai_error_message

        return JSONResponse(
            status_code=502,
            content={"detail": openai_error_message(exc)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Unexpected server error: {exc}"},
        )

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
