from tgbot.core.query.parser import DistributionQueryParser
from tgbot.misc.logger import logger


class DistributionQuery(DistributionQueryParser):
    def __init__(self, query_text: str):
        super().__init__(query_text)

    def query(self):
        return self.query

    def get_pretty_query(self):
        if not self.data:
            self.parse_all_data()

        logger.info(self.data)

        if self.data.range_data:
            return f"range({self.data.range_data.start}, {self.data.range_data.end}) +{self.data.count_choices}"
        return None

if __name__ == "__main__":
    """local test"""

    test_queries = [
        "range(1, 10) + 5 some text",
        "range(5, 15) - 5",
        "simple + 3",
        "just text"
    ]

    for query in test_queries:
        pq = DistributionQuery(query)
        print(f"Query: {query}")
        print(f"Data: {pq.parse_all_data()}")