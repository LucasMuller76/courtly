from typing import Generator, Optional

from fastapi import Depends, HTTPException, Cookie, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import User, Club


def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Lê o JWT do cookie httpOnly e retorna o usuário logado.
    Redireciona para /login se não autenticado.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"},
        )
    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                headers={"Location": "/login"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"},
        )
    return user


def get_current_club(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Club:
    """
    Retorna o clube do usuário logado.
    Se ainda não tem clube, redireciona para o onboarding.
    """
    club = db.query(Club).filter(Club.user_id == current_user.id).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/onboarding"},
        )
    return club