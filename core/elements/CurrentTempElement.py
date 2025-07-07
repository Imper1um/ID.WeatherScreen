from datetime import datetime
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import ElementRefresh
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers, Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class CurrentTempElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        display = "--°"
        if (current.CurrentTemp is not None):
            temp = current.CurrentTemp
            display = f"{temp:.1f}°"

        store.CurrentTemp = self.Wrapper.TextElement(display, self.Settings.CurrentTemp)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        if (not store.CurrentTemp or store.CurrentTemp.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        display = "--°"
        if (current.CurrentTemp is not None):
            temp = current.CurrentTemp
            display = f"{temp:.1f}°"

        store.CurrentTemp.UpdateText(display)
        return self.ElementRefresh