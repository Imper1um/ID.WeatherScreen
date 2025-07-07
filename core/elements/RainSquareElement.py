from config.SettingsEnums import PrecipitationType
from .ElementBase import ElementBase
from .ElementRefresh import ElementRefresh
from core.store import WeatherDisplayStore
from core.drawing import CanvasWrapper
from config.WeatherSettings import WeatherSettings
from helpers.Delay import Delay

from data import *

class RainSquareElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainSquare
        if (not config.Enabled):
            return self.ElementRefresh

        if (current.Humidity is None):
            return self.ElementRefresh

        size = config.Size
        store.RainSquare.FillRect = self.Wrapper.Rectangle(config.X + 1, config.Y + size, config.X + size - 2, config.Y + size - 2, fillColor="#00BFFF",outlineColor=None)
        store.RainSquare.OutsideRect = self.Wrapper.Rectangle(config.X, config.Y, config.X + size, config.Y + size, outlineColor="white", borderWidth=2)
        store.RainSquare.Emoji = self.Wrapper.EmojiElement("💧", config.Emoji, xOffset = config.X + size // 2, yOffset = config.Y + size // 2)
        store.RainSquare.Text = self.Wrapper.TextElement("--", config.Text, xOffset = config.X + size // 2, yOffset = config.Y + size // 2)

        return self.Refresh(store,forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainSquare
        if (not config.Enabled):
            return self.ElementRefresh

        if (not store.RainSquare.FillRect or store.RainSquare.FillRect.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        max_inches = config.MaxRain
        size = config.Size
        x = config.X
        y = config.Y

        rain_inches = current.Rain
        max_inches = config.MaxRain
        rain_inches = min(max(rain_inches, 0), max_inches)
        fill_ratio = rain_inches / max_inches

        rainAddon = '"' if self.Settings.Precipitation == PrecipitationType.IN else 'MM'

        fill_height = int(size * fill_ratio)
        top_fill_y = y + size - fill_height

        store.RainSquare.FillRect.MoveDouble(x, top_fill_y, x + size, y + size)
        label = F"--{rainAddon}"
        if (current.Rain is not None):
            label = F"{current.Rain:.2f}{rainAddon}"

        store.RainSquare.Text.UpdateText(label)

        return self.ElementRefresh