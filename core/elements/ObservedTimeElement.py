from datetime import datetime
from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers, Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class ObservedTimeElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(15)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        store.ObservedTime = self.Wrapper.FormattedTextElement(current.ObservedTimeLocal, self.Settings.Observed)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.ObservedTime or store.ObservedTime.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        now = datetime.now()
        store.ObservedTime.UpdateText(DateTimeHelpers.HourSafeToString(now, self.Settings.Observed.Format))
        return self.ElementRefresh