class DistributionException:
    def __init__(self, message):
        self._message = message

    @property
    def text(self):
        return self._message

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text
