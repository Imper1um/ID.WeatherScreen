from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class WeatherEmojiElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not self.Settings.CurrentTempEmoji.Enabled):
            return self.ElementRefresh

        emoji = current.Conditions.GetEmoji()
        store.WeatherEmoji = self.Wrapper.StackedEmojiElement(emoji, self.Settings.CurrentTempEmoji)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.WeatherEmoji or store.WeatherEmoji.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)
        if (not self.Settings.CurrentTempEmoji.Enabled):
            store.WeatherEmoji.Delete()
            store.WeatherEmoji = None
            return self.ElementRefresh

        emoji = current.Conditions.GetEmoji()

        store.WeatherEmoji.Front.UpdateText(emoji.Front)
        store.WeatherEmoji.Middle.UpdateText(emoji.Middle)
        store.WeatherEmoji.Back.UpdateText(emoji.Back)
        return self.ElementRefresh