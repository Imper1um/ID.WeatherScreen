from datetime import datetime
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements import ElementRefresh
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers
from core.store.WeatherDisplayStore import WeatherDisplayStore

class UptimeElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        self.Start = datetime.now()

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        uptime = F"Uptime: {DateTimeHelpers.GetReadableTimeBetween(self.Start)}"
        store.Uptime = self.Wrapper.TextElement(uptime, self.Settings.Uptime)
        return ElementRefresh.NextSecond()

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.Uptime or store.Uptime.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        uptime = F"Uptime: {DateTimeHelpers.GetReadableTimeBetween(self.Start)}"
        store.Uptime.UpdateText(uptime)
        return ElementRefresh.NextSecond()