import re
from tgbot.core.config import DistributionConfig
from tgbot.db.models import DistributionRange
from tgbot.query.exceptions import DistributionParserException
from dataclasses import dataclass
from aiogram.utils.i18n import gettext as _


from typing import Pattern


@dataclass
class DistributionQueryData:
    range_data: DistributionRange | None
    count_choices: int


class DistributionQueryParser:
    RANGE_PATTERN: Pattern = re.compile(
        r"(?:(?P<start>\d+)\s*[-,\s]\s*(?P<end>\d+))|"
        r"(?:^\s*(?P<single_end>\d+)\s*(?:\+.*)?$)"
    )
    COUNT_CHOICES_PATTERN: Pattern = re.compile(r"\+\s*(\d+)")

    def __init__(self, query_text: str):
        self.query_text = query_text.strip()
        self._config = DistributionConfig()

    def parse_range(self) -> DistributionRange:
        match = self.RANGE_PATTERN.search(self.query_text)
        if not match:
            raise DistributionParserException()

        groups = match.groupdict()

        if groups['single_end']:
            start, end = 1, int(groups['single_end'])
        else:
            start, end = int(groups['start']), int(groups['end'])

        if end == 1:
            raise DistributionParserException(_("количество вариантов должно быть больше 1"))
        if start >= end:
            raise DistributionParserException(_("начальное значение диапазона x должно быть меньше конечного y"))

        range_size = end - start + 1
        if range_size > self._config.max_choices:
            raise DistributionParserException(
                _("максимальное количество выборов - {max_choices}").format(
                    max_choices=self._config.max_choices
                )
            )

        return DistributionRange(start=start, end=end)


    def parse_count_choices(self) -> int:
        count_choices_search = self.COUNT_CHOICES_PATTERN.search(self.query_text)
        if count_choices_search:
            return int(count_choices_search.group(1))

        return 1

    def parse_all_data(self) -> DistributionQueryData:
        range_data = self.parse_range()
        count_choices = self.parse_count_choices()

        range_size = range_data.end - range_data.start + 1
        if count_choices > range_size:
            raise DistributionParserException(
                _(
                "количество выборов (+{count_choices}) не может превышать размер диапазона ({range_size})"
                ).format(count_choices=count_choices, range_size=range_size)
            )

        return DistributionQueryData(range_data=range_data, count_choices=count_choices)