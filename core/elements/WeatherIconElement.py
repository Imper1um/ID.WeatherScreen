from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class WeatherIconElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not self.Settings.CurrentTempIcon.Enabled):
            return self.ElementRefresh

        emoji = current.Conditions.GetIcon()

        basePath = self.Config._basePath
        folder = "/assets/icons/"
        stoke = "-Outline" if self.Settings.CurrentTempIcon.Stroke else ""
        icon = F'Icon-{emoji.Icon.value}{stoke}.png'
        path = F'{basePath}{folder}{icon}'

        store.WeatherIcon = self.Wrapper.StackedIconElement(path, emoji, self.Settings.CurrentTempIcon)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.WeatherIcon or store.WeatherIcon.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)
        if (not self.Settings.CurrentTempIcon.Enabled):
            store.WeatherIcon.Delete()
            store.WeatherIcon = None
            return self.ElementRefresh

        emoji = current.Conditions.GetIcon()

        basePath = self.Config._basePath
        folder = "/assets/icons/"
        stoke = "-Outline" if self.Settings.CurrentTempIcon.Stroke else ""
        icon = F'Icon-{emoji.Icon.value}{stoke}.png'
        path = F'{basePath}{folder}{icon}'

        store.WeatherIcon.Front.UpdateText(emoji.Front)
        store.WeatherIcon.Middle.UpdateText(emoji.Middle)
        store.WeatherIcon.Back.ChangeImage(path, self.Settings.CurrentTempIcon.Width, self.Settings.CurrentTempIcon.Height)
        return self.ElementRefresh