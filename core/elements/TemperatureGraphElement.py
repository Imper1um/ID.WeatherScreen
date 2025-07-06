from collections import defaultdict
from core.store import WeatherDisplayStore
from . import ElementRefresh, ElementBase
from .ElementRefresh import *
from helpers import Delay
from core.drawing import CanvasWrapper
from config import WeatherSettings
from data import *

def GetColorForTemp(temp, low, high):
    ratio = (temp - low) / max(high - low, 1)
    ratio = max(0.0, min(1.0, ratio))

    red = int(255 * ratio)
    blue = int(255 * (1 - ratio))
    green = 0

    return f'#{red:02x}{green:02x}{blue:02x}'

class TemperatureGraphElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings
        er = ElementRefresh(ElementRefresh.OnUpdateHistoryData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(5)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.TemperatureGraph
        if (not config.Enabled):
            return self.ElementRefresh

        x = config.X
        y = config.Y
        width = config.Width
        height = config.Height

        self.Wrapper.Line(x, y, x+width, y, fillColor="white", width=2, smooth=True)
        self.Wrapper.Line(x, y+height, x+width, y+height, fillColor="white", width=2, smooth=True)

        return self.Refresh(store, forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> int:
        config = self.Settings.TemperatureGraph
        if (not config.Enabled):
            return self.ElementRefresh

        for i in store.TemperatureGraph.ConnectingLines:
            i.Delete()
        for i in store.TemperatureGraph.Points:
            i.Delete()

        store.TemperatureGraph.ConnectingLines.clear()
        store.TemperatureGraph.Points.clear()

        now = datetime.now()
        x = config.X
        y = config.Y
        width = config.Width
        height = config.Height

        hourlyTemps = defaultdict(list)

        minTime = now.replace(minute=0,second=0,microsecond=0) - timedelta(hours=24)
        high = forecast.Daytime.High
        low = forecast.Nighttime.Low
        tempRange = max(high - low, 1)
        tempPoints = []
        coords = []

        for line in history.Lines:
            utcTimestamp = line.ObservedTimeUtc.replace(tzinfo=None)
            hourBucket = utcTimestamp.replace(minute=0,second=0,microsecond=0)
            if minTime <= hourBucket <= now:
                hourlyTemps[hourBucket].append(line.CurrentTemp)

        for i in range(24):
            hour = now - timedelta(hours=23-i)
            bucket = hour.replace(minute=0, second=0, microsecond=0)
            values = hourlyTemps.get(bucket, [])
            avgTemp = sum(values) / len(values) if values else None
            tempPoints.append(avgTemp)

            xPos = x + i * (width / 23)
            if avgTemp is not None:
                norm = (avgTemp - low) / tempRange
                yPos = y + height * (1 - norm)
            else:
                yPos = None
            coords.append((xPos, yPos))

        prevValidIndex = None

        for i, (xCur, yCur) in enumerate(coords):
            if yCur is not None:
                store.TemperatureGraph.Points.append(self.Wrapper.Oval(xCur - 2, yCur - 2, xCur + 2, yCur + 2, fillColor="white", outlineColor=""))

                if prevValidIndex is not None:
                    xPrev, yPrev = coords[prevValidIndex]
                    avgTemp = (tempPoints[prevValidIndex] + tempPoints[i]) / 2
                    color = GetColorForTemp(avgTemp, low, high)
                    store.TemperatureGraph.ConnectingLines.append(self.Wrapper.Line(xPrev, yPrev, xCur, yCur, fillColor=color, width=2, smooth=True))

                prevValidIndex = i

        return self.ElementRefresh