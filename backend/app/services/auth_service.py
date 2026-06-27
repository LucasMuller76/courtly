import re
import unicodedata
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Club, User

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Senha ────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
    )
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ── Slug ──────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Converte texto para slug ASCII seguro para URL."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


# ── Verificações de disponibilidade ──────────────────────────────────────────

def is_email_available(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is None


def is_slug_available(db: Session, slug: str) -> bool:
    return db.query(Club).filter(Club.slug == slug).first() is None


# ── Criação de conta ─────────────────────────────────────────────────────────

def create_user_and_club(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    club_name: str,
    club_slug: str,
) -> tuple[User, Club]:
    """Cria usuário e clube de forma atômica (mesma transação)."""
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.flush()  # gera o UUID do usuário sem commitar ainda

    club = Club(
        user_id=user.id,
        name=club_name,
        slug=club_slug,
    )
    db.add(club)
    db.commit()
    db.refresh(user)
    db.refresh(club)
    return user, club


# ── Autenticação ──────────────────────────────────────────────────────────────

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user