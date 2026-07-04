from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="open",
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="low",
    )

    assignee: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    source_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
