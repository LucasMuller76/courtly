from fastapi import APIRouter, Depends, HTTPException, Response, status
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest
from app.services import auth_service

router = APIRouter()

logger = logging.getLogger("courtly")

_COOKIE_NAME = "courtly_token"
_COOKIE_MAX_AGE = 60 * 60 * 24  # 24 horas em segundos


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=_COOKIE_MAX_AGE,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MeResponse)
def register(
    body: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    if not auth_service.is_email_available(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está em uso.",
        )
    if not auth_service.is_slug_available(db, body.club_slug):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este endereço de clube já está em uso. Escolha outro.",
        )

    try:
        user, club = auth_service.create_user_and_club(
            db,
            name=body.name,
            email=body.email,
            password=body.password,
            club_name=body.club_name,
            club_slug=body.club_slug,
        )
    except IntegrityError:
        # Pode haver condição de corrida entre a checagem de disponibilidade e o commit
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dados em conflito (e-mail ou endereço de clube já em uso).",
        )

    token = auth_service.create_access_token(str(user.id))
    _set_auth_cookie(response, token)
    logger.info("Novo usuário registrado: %s", user.email)
    return {"user": user, "club": club}


@router.post("/login")
def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    token = auth_service.create_access_token(str(user.id))
    _set_auth_cookie(response, token)
    logger.info("Login realizado: %s", user.email)
    return {"message": "Login realizado com sucesso."}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=_COOKIE_NAME, path="/")
    logger.info("Logout realizado")
    return {"message": "Logout realizado."}


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return {"user": current_user, "club": current_user.club}