from datetime import datetime
from logging import Formatter

import pytz

ZONE = "Europe/Kyiv"


class KyivTimeFormatter(Formatter):
    """Setting Kyiv time."""

    def formatTime(self, record, datefmt=None) -> str:
        kyiv_time = datetime.now(tz=pytz.timezone(zone=ZONE)).replace(tzinfo=None)
        return kyiv_time.strftime("%Y-%m-%d %H:%M:%S")
