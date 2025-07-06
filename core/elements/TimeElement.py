from datetime import datetime
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementBase import ElementBase
from core.elements.ElementRefresh import ElementRefresh
from data import *
from helpers import DateTimeHelpers
from core.store.WeatherDisplayStore import WeatherDisplayStore

class TimeElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        now = datetime.now()
        store.Time = self.Wrapper.FormattedTextElement(now, self.Settings.Time)
        return ElementRefresh.NextSecond()

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        if (not store.Time or store.Time.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        now = datetime.now()
        store.DayOfWeek.UpdateText(DateTimeHelpers.HourSafeToString(now, self.Settings.Time.Format))
        return ElementRefresh.NextSecond()