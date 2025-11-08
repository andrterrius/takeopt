from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from aiogram.types import User


class DBUser(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    username: Mapped[str | None] = mapped_column(String(64))

    choices: Mapped[List["DBChoice"]] = relationship("DBChoice", back_populates="user")
    distributions: Mapped[List["DBDistribution"]] = relationship("DBDistribution", back_populates="creator")


    @classmethod
    def from_aiogram(cls, user: User) -> DBUser:
        return cls(id=user.id, name=user.full_name, username=user.username)
