from typing import Optional
from core.drawing.ElementStore import ElementStore

class RainForecastGraphStore:
    def __init__(self):
        self.CloudGradientLines:list[ElementStore] = []
        self.AmbientLightLines:list[ElementStore] = []
        self.PrecipitationAmounts:list[ElementStore] = []
        self.PrecipitationChances:list[ElementStore] = []
        self.WeatherEmojis:list[ElementStore] = []
        self.CloudCoverPercentages:list[ElementStore] = []
        self.HourLabels:list[ElementStore] = []
        self.TopLine:Optional[ElementStore] = None
        self.BottomLine:Optional[ElementStore] = None
        self.NoRainWarning:Optional[ElementStore] = None

    def Clear(self):
        for e in self.CloudGradientLines:
            e.Delete()
        self.CloudGradientLines.clear()
        for e in self.AmbientLightLines:
            e.Delete()
        self.AmbientLightLines.clear()
        for e in self.PrecipitationAmounts:
            e.Delete()
        self.PrecipitationAmounts.clear()
        for e in self.PrecipitationChances:
            e.Delete()
        self.PrecipitationChances.clear()
        for e in self.WeatherEmojis:
            e.Delete()
        self.WeatherEmojis.clear()
        for e in self.CloudCoverPercentages:
            e.Delete()
        self.CloudCoverPercentages.clear()
        for e in self.HourLabels:
            e.Delete()
        self.HourLabels.clear()

        if (self.TopLine is not None):
            self.TopLine.Delete()

        if (self.BottomLine is not None):
            self.BottomLine.Delete()

        if (self.NoRainWarning is not None):
            self.NoRainWarning.Delete()

