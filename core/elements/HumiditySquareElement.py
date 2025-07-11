from .ElementBase import ElementBase
from .ElementRefresh import ElementRefresh
from core.drawing import CanvasWrapper
from config import WeatherConfig, WeatherSettings
from helpers import Delay
from data import *
from core.store.WeatherDisplayStore import WeatherDisplayStore

class HumiditySquareElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.HumiditySquare
        if (not config.Enabled):
            return self.ElementRefresh

        if (current.Humidity is None):
            return self.ElementRefresh

        size = config.Size
        store.HumiditySquare.FillRect = self.Wrapper.Rectangle(config.X + 1, config.Y + size, config.X + size - 2, config.Y + size - 2, fillColor="#00BFFF",outlineColor=None)
        store.HumiditySquare.OutsideRect = self.Wrapper.Rectangle(config.X, config.Y, config.X + size, config.Y + size, outlineColor="white", borderWidth=2)
        store.HumiditySquare.Emoji = self.Wrapper.EmojiElement("💦", config.Emoji, xOffset = config.X + size // 2, yOffset = config.Y + size // 2)
        store.HumiditySquare.Text = self.Wrapper.TextElement("--%", config.Text, xOffset = config.X + size // 2, yOffset = config.Y + size // 2)

        return self.Refresh(store,forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.HumiditySquare
        if (not config.Enabled):
            return self.ElementRefresh

        if (not store.HumiditySquare.FillRect or store.HumiditySquare.FillRect.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        humidity = current.Humidity if current.Humidity is not None else 0.0
        x = config.X
        y = config.Y
        size = config.Size

        fill_ratio = humidity / 100
        fill_height = int(size * fill_ratio)
        top_fill_y = y + size - fill_height

        store.HumiditySquare.FillRect.MoveDouble(x + 1, top_fill_y, x + size - 2, y + size - 2)
        label = "--%"
        if (current.Humidity is not None):
            label = F"{current.Humidity}%"

        store.HumiditySquare.Text.UpdateText(label)

        return self.ElementRefresh
