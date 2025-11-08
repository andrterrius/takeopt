from tgbot.core.query.parser import DistributionQueryParser, DistributionQueryData
from tgbot.misc.logger import logger


class DistributionQuery:
    def __init__(self, query_text: str):
        self._parser = DistributionQueryParser(query_text)
        self._data = None

    @property
    def data(self) -> DistributionQueryData:
        if self._data is None:
            self._data = self._parser.parse_all_data()
        return self._data

    def get_pretty_query(self) -> str:
        return f"{self.data.range_data.start} {self.data.range_data.end} +{self.data.count_choices}"