from contextlib import asynccontextmanager

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.routers import auth as auth_router
from app.routers import courts as courts_router


# Logger
logger = logging.getLogger("courtly")
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🎾 Courtly API iniciando...")
    yield
    print("🎾 Courtly API encerrando...")


app = FastAPI(
    title="Courtly API",
    version="0.1.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)


@app.exception_handler(IntegrityError)
def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    logger.exception("Database integrity error")
    return JSONResponse(
        status_code=409,
        content={"detail": "Database constraint violation."},
    )


@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "courtly", "version": "0.1.0"}


app.include_router(auth_router.router,   prefix="/api/v1/auth",   tags=["auth"])
app.include_router(courts_router.router, prefix="/api/v1/courts", tags=["courts"])