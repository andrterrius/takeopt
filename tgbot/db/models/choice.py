from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import JSON, BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin


class DBChoice(TimestampMixin, Base):
    __tablename__ = "choices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))

    user: Mapped["DBUser"] = relationship("DBUser", back_populates="choices")
