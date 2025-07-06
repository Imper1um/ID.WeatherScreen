from datetime import datetime
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers, Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class SourceElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(15)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        store.Source = self.Wrapper.TextElement(F"Source: {current.Source}", self.Settings.Source)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.Source or store.Source.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        store.Source.UpdateText(F"Source: {current.Source}")
        return self.ElementRefresh