from core.elements.ElementBase import ElementBase
from core.elements.ElementRefresh import ElementRefresh
from core.store.WeatherDisplayStore import WeatherDisplayStore
from data import *

class WeatherScheduleItem:
    def __init__(self, elementRefresh:ElementRefresh, elementBase:ElementBase):
        self.IsSatisfied = False
        self.ElementBase = elementBase
        self.ElementRefresh = elementRefresh

    def Call(self, store: WeatherDisplayStore, forecast:ForecastData, current:CurrentData, history:HistoryData, sun:SunData) -> ElementRefresh:
        r = self.ElementBase.Refresh(store, forecast, current, history, sun)
        self.IsSatisfied = True
        return r