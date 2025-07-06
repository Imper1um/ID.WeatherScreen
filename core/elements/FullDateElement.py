from datetime import datetime, timedelta
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementBase import ElementBase
from core.elements.ElementRefresh import ElementRefresh
from data import *
from helpers import DateTimeHelpers
from core.store.WeatherDisplayStore import WeatherDisplayStore


class FullDateElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        now = datetime.now()
        store.FullDate = self.Wrapper.FormattedTextElement(now, self.Settings.FullDate)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        return ElementRefresh.OnMidnight()

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.FullDate or store.FullDate.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        now = datetime.now()
        store.DayOfWeek.UpdateText(DateTimeHelpers.HourSafeToString(now, self.Settings.FullDate.Format))
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        return ElementRefresh.OnMidnight()