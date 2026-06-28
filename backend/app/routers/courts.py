import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
import logging
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_club
from app.models import Club, Court, Reservation
from app.schemas.court import CourtCreate, CourtOut, CourtUpdate

router = APIRouter()
logger = logging.getLogger("courtly")


def _get_court_or_404(
    db: Session, court_id: uuid.UUID, club_id: uuid.UUID
) -> Court:
    court = (
        db.query(Court)
        .filter(Court.id == court_id, Court.club_id == club_id)
        .first()
    )
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )
    return court


@router.get("/", response_model=List[CourtOut])
def list_courts(
    club: Club = Depends(get_current_club),
    db: Session = Depends(get_db),
):
    return (
        db.query(Court)
        .filter(Court.club_id == club.id)
        .order_by(Court.name)
        .all()
    )


@router.post("/", response_model=CourtOut, status_code=status.HTTP_201_CREATED)
def create_court(
    body: CourtCreate,
    club: Club = Depends(get_current_club),
    db: Session = Depends(get_db),
):
    court = Court(
        club_id=club.id,
        name=body.name,
        price_per_hour=body.price_per_hour,
    )
    db.add(court)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito ao criar quadra.",
        )
    except Exception:
        db.rollback()
        logger.exception("Erro ao criar quadra")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar quadra.",
        )
    db.refresh(court)
    return court


@router.patch("/{court_id}", response_model=CourtOut)
def update_court(
    court_id: uuid.UUID,
    body: CourtUpdate,
    club: Club = Depends(get_current_club),
    db: Session = Depends(get_db),
):
    court = _get_court_or_404(db, court_id, club.id)

    allowed = {"name", "price_per_hour", "is_active"}
    for field, value in body.model_dump(exclude_unset=True).items():
        if field in allowed:
            setattr(court, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito ao atualizar quadra.",
        )
    except Exception:
        db.rollback()
        logger.exception("Erro ao atualizar quadra %s", court_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar quadra.",
        )
    db.refresh(court)
    return court


@router.delete("/{court_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_court(
    court_id: uuid.UUID,
    club: Club = Depends(get_current_club),
    db: Session = Depends(get_db),
):
    court = _get_court_or_404(db, court_id, club.id)

    # Bloqueia exclusão se houver reservas futuras confirmadas
    has_future = (
        db.query(Reservation)
        .filter(
            Reservation.court_id == court.id,
            Reservation.starts_at > datetime.now(timezone.utc),
            Reservation.status == "confirmed",
        )
        .first()
    )
    if has_future:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Esta quadra possui reservas futuras confirmadas. "
                "Cancele-as antes de excluir a quadra."
            ),
        )

    try:
        db.delete(court)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito ao excluir quadra.",
        )
    except Exception:
        db.rollback()
        logger.exception("Erro ao excluir quadra %s", court_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir quadra.",
        )