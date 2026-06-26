from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🎾 Courtly iniciando...")
    # Aqui vamos iniciar o APScheduler nas próximas etapas
    yield
    print("🎾 Courtly encerrando...")


app = FastAPI(
    title="Courtly",
    description="Secretária Virtual para Clubes de Padel",
    version="0.1.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "courtly", "version": "0.1.0"}


# ── Raiz: redireciona para o painel ou login ──────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # Por ora redireciona para o login
    # Depois vamos verificar o cookie e redirecionar para /admin se logado
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ── Routers (serão adicionados progressivamente) ──────────────────────────────
# from app.routers import auth, admin, public, webhooks
# app.include_router(auth.router)
# app.include_router(admin.router, prefix="/admin")
# app.include_router(public.router)
# app.include_router(webhooks.router, prefix="/webhooks")