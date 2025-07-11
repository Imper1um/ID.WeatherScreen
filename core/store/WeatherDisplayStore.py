from typing import Optional
from core.drawing.ElementStore import ElementStore
from core.store.EmojiStore import EmojiStore
from .HumiditySquareStore import HumiditySquareStore
from .RainForecastGraphStore import RainForecastGraphStore
from .RainSquareStore import RainSquareStore
from .TemperatureGraphStore import TemperatureGraphStore
from .WindIndicatorStore import WindIndicatorStore

class WeatherDisplayStore:
    def __init__(self):
        self.Background: Optional[ElementStore] = None

        self.DayOfWeek: Optional[ElementStore] = None
        self.FullDate: Optional[ElementStore] = None
        self.Time: Optional[ElementStore] = None
        self.Uptime: Optional[ElementStore] = None
        self.LastUpdate: Optional[ElementStore] = None
        self.ObservedTime: Optional[ElementStore] = None
        self.Source: Optional[ElementStore] = None
        self.ImageTags: Optional[ElementStore] = None
        self.Station: Optional[ElementStore] = None
        self.CurrentTemp: Optional[ElementStore] = None
        self.FeelsLike: Optional[ElementStore] = None
        self.WeatherEmoji: Optional[EmojiStore] = None
        self.WeatherIcon: Optional[EmojiStore] = None
        self.High: Optional[ElementStore] = None
        self.Low: Optional[ElementStore] = None

        self.HumiditySquare = HumiditySquareStore()
        self.RainForecastGraph = RainForecastGraphStore()
        self.RainSquare = RainSquareStore()
        self.TemperatureGraph = TemperatureGraphStore()
        self.WindIndicator = WindIndicatorStore()
        