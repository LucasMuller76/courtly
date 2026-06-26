from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # reconecta automaticamente se a conexão cair
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency do FastAPI: abre e fecha a sessão do banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()