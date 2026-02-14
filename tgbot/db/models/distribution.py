import json
import uuid as uuid_pkg

from sqlalchemy import text
from sqlalchemy import JSON, BigInteger, ForeignKey
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID



from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin

from dataclasses import dataclass


class DistributionRange:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end #храним в базе значение с границей включительно

    def to_dict(self):
        return {'start': self.start, 'end': self.end}

    @classmethod
    def from_dict(cls, data):
        return cls(start=data['start'], end=data['end'])


class DistributionRangeType(TypeDecorator):
    impl = JSON

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, DistributionRange):
            return value.to_dict()
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            value = json.loads(value)
        return DistributionRange.from_dict(value)


class DBDistribution(TimestampMixin, Base):
    __tablename__ = "distributions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid_pkg.uuid4,
        server_default=text("gen_random_uuid()")
    )
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    query: Mapped[str]
    range_data: Mapped[DistributionRange] = mapped_column(DistributionRangeType)
    count_choices: Mapped[int] = mapped_column(default=1)

    creator: Mapped["DBUser"] = relationship("DBUser", back_populates="distributions")
