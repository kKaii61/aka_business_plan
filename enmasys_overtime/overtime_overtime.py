import logging

_logger = logging.getLogger(__name__)


class OvertimeOvertime:
    _overtime_date = False
    _overtime_start = False
    _overtime_end = False

    def __init__(self, over_time_date=False, overtime_start=False, overtime_end=False):
        self._overtime_date = over_time_date
        self._overtime_start = overtime_start
        self._overtime_end = overtime_end

    def check_overlapped(self, range_start, range_to):
        _start = self._overtime_start
        _end = self._overtime_end
        if not _start or not _end or not range_start or not range_to:
            return False
        if range_start > range_to or _start > _end:
            return False
        if _start < range_to and _end > range_start:
            return True
        return False
