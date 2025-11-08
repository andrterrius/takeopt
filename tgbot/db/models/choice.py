from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import Index, JSON, BigInteger, ForeignKey, Integer, String, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin


class DBChoice(TimestampMixin, Base):
    __tablename__ = "choices"
    __table_args__ = (
        Index('uq_active_choice', 'distribution_id', 'button_index',
              unique=True,
              postgresql_where=text('active = true')),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    distribution_id: Mapped[int]
    button_index: Mapped[int]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    active = mapped_column(Boolean, default=True)

    user: Mapped["DBUser"] = relationship("DBUser", back_populates="choices")
