import re
from tgbot.config import DistributionConfig
from tgbot.db.models import DistributionRange
from tgbot.core.query.exceptions import DistributionException
from dataclasses import dataclass


@dataclass
class DistributionQueryData:
    range_data: DistributionRange | None
    count_choices: int


class DistributionQueryParser:
    def __init__(self, query_text: str):
        self.query = query_text
        self.data = None
        self._config = DistributionConfig()

    def parse_range(self) -> DistributionRange | DistributionException:
        range_pattern = r"range\((?P<start>\d+),\s*(?P<end>\d+)\)"
        range_search = re.search(range_pattern, self.query)
        if range_search:
            range_group_dict = range_search.groupdict()
            start = int(range_group_dict['start'])
            end = int(range_group_dict['end'])
            if start >= end:
                return DistributionException("стартовое значение в range должно быть меньше или равно конечному")
            if end - start > self._config.max_votes:
                return DistributionException(f"максимальное количество выборов - {self._config.max_votes}")

            return DistributionRange(start=start, end=end)

        return DistributionException(
            f"проверьте правильность вввода промежутка: range(start, end), где start, end - целые неотриц. числа, start < end и end-start < {self._config.max_votes}")

    def parse_count_choices(self) -> int:
        count_choices = r"(?<!\S)\+\s*(\d+)(?!\S)"
        count_choices_search = re.search(count_choices, self.query)
        if count_choices_search:
            return int(count_choices_search.group(1))

        return 1

    def parse_all_data(self) -> DistributionQueryData:
        if not self.data:
            range_data = self.parse_range()
            count_choices = self.parse_count_choices()

            if isinstance(range_data, DistributionRange):
                range_size = range_data.end - range_data.start
                if count_choices > range_size:
                    return DistributionException(
                        f"количество выборов (+{count_choices}) не может превышать размер диапазона ({range_size})")
            else:
                return range_data  # возвращаем ошибку

            self.data = DistributionQueryData(range_data=self.parse_range(), count_choices=self.parse_count_choices())
        return self.data
