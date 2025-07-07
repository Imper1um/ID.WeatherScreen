from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import Delay, WeatherHelpers
from core.store.WeatherDisplayStore import WeatherDisplayStore

class WeatherEmojiElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:

        now = datetime.now()
        state = current.State
        emoji = WeatherHelpers.GetWeatherEmoji(state, now, forecast, sunData)
        store.WeatherEmoji = self.Wrapper.EmojiElement(emoji["Emoji"], self.Settings.CurrentTempEmoji)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.WeatherEmoji or store.WeatherEmoji.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        now = datetime.now()
        state = current.State
        emoji = WeatherHelpers.GetWeatherEmoji(state, now, forecast, sunData)

        store.WeatherEmoji.UpdateText(emoji["Emoji"])
        return self.ElementRefresh