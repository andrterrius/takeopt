from sqlalchemy import JSON, BigInteger, ForeignKey
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship


from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin

from dataclasses import dataclass

@dataclass
class DistributionRange:
    start: int
    end: int


class DistributionRangeType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, DistributionRange):
            return {'start': value.start, 'end': value.end}
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return DistributionRange(start=value['start'], end=value['end'])

class DBDistribution(TimestampMixin, Base):
    __tablename__ = "distributions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    query: Mapped[str]
    range_data: Mapped[DistributionRange] = mapped_column(DistributionRangeType)
    count_choices: Mapped[int] = mapped_column(default=1)

    creator: Mapped["DBUser"] = relationship("DBUser", back_populates="distributions")
