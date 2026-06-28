import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Boolean, Text,
    DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────
# USER  (dono do clube)
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    club: Mapped[Optional["Club"]] = relationship(
        "Club", back_populates="user", uselist=False
    )


# ─────────────────────────────────────────
# CLUB  (um por usuário no MVP)
# ─────────────────────────────────────────
class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,   # ← garante 1 clube por usuário
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(30))
    timezone: Mapped[str] = mapped_column(
        String(50), default="America/Sao_Paulo"
    )
    address: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {
            "open_time": "07:00",
            "close_time": "23:00",
            "slot_duration_minutes": 60,
            "min_advance_minutes": 60,
            "max_advance_days": 30,
            "cancellation_hours": 2,
        },
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="club")
    courts: Mapped[List["Court"]] = relationship(
        "Court", back_populates="club", cascade="all, delete-orphan"
    )
    players: Mapped[List["Player"]] = relationship(
        "Player", back_populates="club", cascade="all, delete-orphan"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="club"
    )
    waiting_list: Mapped[List["WaitingList"]] = relationship(
        "WaitingList", back_populates="club"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="club"
    )
    whatsapp_conversations: Mapped[List["WhatsappConversation"]] = relationship(
        "WhatsappConversation", back_populates="club"
    )


# ─────────────────────────────────────────
# COURT  (quadras do clube)
# ─────────────────────────────────────────
class Court(Base):
    __tablename__ = "courts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_per_hour: Mapped[Optional[int]] = mapped_column(Integer)  # em centavos
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    club: Mapped["Club"] = relationship("Club", back_populates="courts")
    blocked_slots: Mapped[List["CourtBlockedSlot"]] = relationship(
        "CourtBlockedSlot", back_populates="court", cascade="all, delete-orphan"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="court"
    )


# ─────────────────────────────────────────
# COURT BLOCKED SLOT  (bloqueios manuais)
# ─────────────────────────────────────────
class CourtBlockedSlot(Base):
    __tablename__ = "court_blocked_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courts.id", ondelete="CASCADE"),
        nullable=False,
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False, index=True
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    court: Mapped["Court"] = relationship("Court", back_populates="blocked_slots")


# ─────────────────────────────────────────
# PLAYER  (jogadores — identificados por telefone)
# ─────────────────────────────────────────
class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("club_id", "phone", name="uq_player_club_phone"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    whatsapp_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    club: Mapped["Club"] = relationship("Club", back_populates="players")
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="player"
    )
    waiting_list: Mapped[List["WaitingList"]] = relationship(
        "WaitingList", back_populates="player"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="player"
    )


# ─────────────────────────────────────────
# RESERVATION
# ─────────────────────────────────────────
class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False, index=True
    )
    court_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # status: confirmed | cancelled | no_show | completed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="confirmed"
    )
    # source: web | whatsapp | manual
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="web"
    )
    total_price: Mapped[Optional[int]] = mapped_column(Integer)  # centavos (futuro)
    confirmation_code: Mapped[str] = mapped_column(
        String(8), unique=True, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    cancelled_by: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    club: Mapped["Club"] = relationship("Club", back_populates="reservations")
    court: Mapped["Court"] = relationship("Court", back_populates="reservations")
    player: Mapped["Player"] = relationship("Player", back_populates="reservations")
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="reservation"
    )


# ─────────────────────────────────────────
# WAITING LIST
# ─────────────────────────────────────────
class WaitingList(Base):
    __tablename__ = "waiting_list"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False, index=True
    )
    court_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courts.id")
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id"), nullable=False
    )
    desired_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    desired_starts_at: Mapped[str] = mapped_column(String(5), nullable=False)  # "HH:MM"
    desired_ends_at: Mapped[str] = mapped_column(String(5), nullable=False)    # "HH:MM"
    # status: waiting | notified | booked | expired
    status: Mapped[str] = mapped_column(String(20), default="waiting")
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    club: Mapped["Club"] = relationship("Club", back_populates="waiting_list")
    player: Mapped["Player"] = relationship("Player", back_populates="waiting_list")


# ─────────────────────────────────────────
# NOTIFICATION  (fila + log em uma tabela)
# ─────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False, index=True
    )
    player_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id")
    )
    reservation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reservations.id")
    )
    # type: confirmation | reminder_24h | reminder_1h | cancellation | waitlist_available
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    # channel: whatsapp | email | sms
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    # status: pending | sent | failed | skipped
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    club: Mapped["Club"] = relationship("Club", back_populates="notifications")
    player: Mapped[Optional["Player"]] = relationship(
        "Player", back_populates="notifications"
    )
    reservation: Mapped[Optional["Reservation"]] = relationship(
        "Reservation", back_populates="notifications"
    )


# ─────────────────────────────────────────
# WHATSAPP CONVERSATION  (estado da conversa)
# ─────────────────────────────────────────
class WhatsappConversation(Base):
    __tablename__ = "whatsapp_conversations"
    __table_args__ = (
        UniqueConstraint(
            "club_id", "player_phone", name="uq_whatsapp_club_phone"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False, index=True
    )
    player_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    # estados: idle | awaiting_date | awaiting_duration | awaiting_slot_choice
    #          | awaiting_name | awaiting_confirmation | done
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="idle")
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    club: Mapped["Club"] = relationship(
        "Club", back_populates="whatsapp_conversations"
    )