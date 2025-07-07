from datetime import datetime, timedelta

class ElementRefresh:
    OnUpdateCurrentData: str = "UpdateCurrentData"
    OnUpdateSunData: str = "UpdateSunData"
    OnUpdateForecastData: str = "UpdateForecastData"
    OnUpdateHistoryData: str = "UpdateHistoryData"
    OnUpdateBackground: str = "UpdateBackground"
    OnTimer: str = "Timer"

    def __init__(self, *reasons: str):
        self.Reasons = reasons
        self.Delay = 1000

    @staticmethod
    def OnMidnight() -> "ElementRefresh":
        er = ElementRefresh(ElementRefresh.OnTimer)
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        er.Delay = int(delta.total_seconds()) * 1000
        return er

    @staticmethod
    def NextHour() -> "ElementRefresh":
        er = ElementRefresh(ElementRefresh.OnTimer)
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        delta = next_hour - now
        er.Delay = int(delta.total_seconds() * 1000)
        return er

    @staticmethod
    def NextMinute() -> "ElementRefresh":
        er = ElementRefresh(ElementRefresh.OnTimer)
        now = datetime.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        delta = next_minute - now
        er.Delay = int(delta.total_seconds() * 1000)
        return er

    @staticmethod
    def NextSecond() -> "ElementRefresh":
        er = ElementRefresh(ElementRefresh.OnTimer)
        now = datetime.now()
        next_second = (now + timedelta(seconds=1)).replace(microsecond=0)
        delta = next_second - now
        er.Delay = int(delta.total_seconds() * 1000)
        return er

    