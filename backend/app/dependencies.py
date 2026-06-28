from typing import Optional
import uuid

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import get_db
from app.models import Club, User


def get_current_user(
    courtly_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Lê o JWT do cookie httpOnly e retorna o usuário logado.
    O nome do parâmetro deve ser idêntico ao nome do cookie.
    """
    if not courtly_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado.",
        )
    try:
        payload = jwt.decode(
            courtly_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )
        try:
            user_uuid = uuid.UUID(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )

    # selectinload carrega o relacionamento club junto com o user
    # evita lazy loading depois que a sessão for fechada
    user = (
        db.query(User)
        .options(selectinload(User.club))
        .filter(User.id == user_uuid)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    return user


def get_current_club(
    current_user: User = Depends(get_current_user),
) -> Club:
    """Retorna o clube do usuário logado (o club já vem carregado via selectinload)."""
    if not current_user.club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum clube associado a este usuário.",
        )
    return current_user.club