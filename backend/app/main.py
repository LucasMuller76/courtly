from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


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

# CORS — permite o frontend Next.js chamar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,   # necessário para cookies httpOnly
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ───────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "courtly", "version": "0.1.0"}


# ── Routers (adicionados progressivamente) ─────────────────
# from app.routers import auth, clubs, courts, reservations, public, webhooks
# app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["auth"])
# app.include_router(clubs.router,        prefix="/api/v1/clubs",        tags=["clubs"])
# app.include_router(courts.router,       prefix="/api/v1/courts",       tags=["courts"])
# app.include_router(reservations.router, prefix="/api/v1/reservations", tags=["reservations"])
# app.include_router(public.router,       prefix="/api/v1/public",       tags=["public"])
# app.include_router(webhooks.router,     prefix="/webhooks",            tags=["webhooks"]) 