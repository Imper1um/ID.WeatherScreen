from datetime import datetime
from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementRefresh import *
from core.elements.ElementBase import ElementBase
from data import *
from helpers import DateTimeHelpers, Delay
from core.store.WeatherDisplayStore import WeatherDisplayStore

class ImageTagsElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather
        er = ElementRefresh(ElementRefresh.OnUpdateBackground, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(15)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not self.Settings.ImageTags.Enabled):
            return self.ElementRefresh
        imageTags = F"Requested Image Tags: {current.LastBackgroundImageTags} // This Image Tags: {current.ThisImageTags}"
        if (current.ImageTagMessage):
            imageTags += F" // Image Message: {current.ImageTagMessage}"
        store.ImageTags = self.Wrapper.TextElement(imageTags, self.Settings.ImageTags)
        return self.ElementRefresh

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        if (not store.ImageTags or store.ImageTags.IsDeleted):
            return self.Initialize(store, forecast, current, history, sunData)

        imageTags = F"Requested Image Tags: {current.LastBackgroundImageTags} // This Image Tags: {current.ThisImageTags}"
        if (current.ImageTagMessage):
            imageTags += F" // Image Message: {current.ImageTagMessage}"
        store.ImageTags.UpdateText(imageTags)
        return self.ElementRefresh