from datetime import datetime, timedelta
from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import ElementRefresh
from core.store.WeatherDisplayStore import WeatherDisplayStore
from data import *
from helpers.DateTimeHelpers import DateTimeHelpers
from .ElementBase import ElementBase

class DayOfWeekElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        now = datetime.now()
        store.DayOfWeek = self.Wrapper.FormattedTextElement(now, self.Settings.DayOfWeek)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        return ElementRefresh.OnMidnight()

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        if (not store.DayOfWeek or store.DayOfWeek.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        now = datetime.now()
        store.DayOfWeek.UpdateText(DateTimeHelpers.HourSafeToString(now, self.Settings.DayOfWeek.Format))
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        return ElementRefresh.OnMidnight()
