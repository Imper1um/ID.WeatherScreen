from datetime import datetime
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers, Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class FeelsLikeElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        display = "Feels Like: --°"
        if (current.FeelsLike is not None):
            temp = current.FeelsLike
            display = f"Feels Like: {temp:.1f}°"

        store.FeelsLike = self.Wrapper.TextElement(display, self.Settings.FeelsLike)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.FeelsLike or store.FeelsLike.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        display = "Feels Like: --°"
        if (current.FeelsLike is not None):
            temp = current.FeelsLike
            display = f"Feels Like: {temp:.1f}°"

        store.FeelsLike.UpdateText(display)
        return self.ElementRefresh