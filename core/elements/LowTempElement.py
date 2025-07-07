from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import ElementRefresh
from core.elements.ElementBase import ElementBase
from data import *
from helpers import Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class LowTempElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateForecastData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromHours(3)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        display = "--°"
        if (forecast.Nighttime.Low is not None):
            temp = forecast.Nighttime.Low
            display = f"{temp:.1f}°"

        store.Low = self.Wrapper.TextElement(display, self.Settings.TempLow)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        if (not store.Low or store.Low.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        display = "--°"
        if (forecast.Nighttime.Low is not None):
            temp = forecast.Nighttime.Low
            display = f"{temp:.1f}°"

        store.Low.UpdateText(display)
        return self.ElementRefresh