import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date

from database import Base
from datetime import datetime, timedelta
from sqlalchemy import DateTime
from datetime import datetime, UTC
import uuid
from datetime import date

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Date,
    ForeignKey
)

default=lambda: datetime.now(UTC) + timedelta(hours=24)


class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    google_id = Column(
        String,
        unique=True,
        nullable=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    profile_picture = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )








# -----------------------------
# Squad
# -----------------------------
class Squad(Base):
    __tablename__ = "squads"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    name = Column(
        String,
        nullable=False
    )

    created_by = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# -----------------------------
# Squad Members
# -----------------------------
class SquadMember(Base):
    __tablename__ = "squad_members"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    squad_id = Column(
        String,
        nullable=False
    )

    user_id = Column(
        String,
        nullable=False
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# -----------------------------
# Invite Links
# -----------------------------
class InviteLink(Base):
    __tablename__ = "invite_links"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    squad_id = Column(
        String,
        nullable=False
    )

    token = Column(
        String,
        unique=True,
        default=lambda: str(uuid.uuid4())
    )

    expires_at = Column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    is_used = Column(
        Boolean,
        default=False
    )

class Habit(Base):
    __tablename__ = "habits"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    squad_id = Column(
        String,
        ForeignKey("squads.id")
    )

    title = Column(
        String,
        nullable=False
    )

    created_by = Column(
        String,
        ForeignKey("users.id")
    )

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    habit_id = Column(
        String,
        ForeignKey("habits.id")
    )

    user_id = Column(
        String,
        ForeignKey("users.id")
    )

    completed = Column(
        Boolean,
        default=False
    )

    date = Column(
        Date,
        default=date.today
    )