from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class HighTempElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateForecastData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromHours(3)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        display = "--°"
        if (forecast.Daytime.High is not None):
            temp = forecast.Daytime.High
            display = f"{temp:.1f}°"

        store.High = self.Wrapper.TextElement(display, self.Settings.TempHigh)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.High or store.High.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        display = "--°"
        if (forecast.Daytime.High is not None):
            temp = forecast.Daytime.High
            display = f"{temp:.1f}°"

        store.High.UpdateText(display)
        return self.ElementRefresh