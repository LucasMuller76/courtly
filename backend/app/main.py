from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🎾 Courtly API iniciando...")
    # APScheduler será inicializado aqui nas próximas etapas
    yield
    print("🎾 Courtly API encerrando...")


app = FastAPI(
    title="Courtly API",
    description="Secretária Virtual para Clubes de Padel",
    version="0.1.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # obrigatório para cookies httpOnly
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "courtly", "version": "0.1.0"}


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])

# Próximas etapas:
# from app.routers import clubs, courts, reservations, public, webhooks
# app.include_router(clubs.router,        prefix="/api/v1/clubs",        tags=["clubs"])
# app.include_router(courts.router,       prefix="/api/v1/courts",       tags=["courts"])
# app.include_router(reservations.router, prefix="/api/v1/reservations", tags=["reservations"])
# app.include_router(public.router,       prefix="/api/v1/public",       tags=["public"])
# app.include_router(webhooks.router,     prefix="/webhooks",            tags=["webhooks"])