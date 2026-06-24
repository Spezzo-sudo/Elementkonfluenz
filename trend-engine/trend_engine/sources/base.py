from .item import SourceItem


class SourceAdapter:
    source_id = "base"

    def collect(self):
        return []


TrendSignal = SourceItem
TrendSource = SourceAdapter
