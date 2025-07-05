from collections import defaultdict
from datetime import datetime, timedelta
from config.SizeElementSettings import SizeElementSettings
from data.ForecastData import ForecastData
from data.HistoryData import HistoryData
from .CanvasWrapper import CanvasWrapper

class TemperatureGraph:
    def GetColorForTemp(temp, low, high):
        ratio = (temp - low) / max(high - low, 1)
        ratio = max(0.0, min(1.0, ratio))

        red = int(255 * ratio)
        blue = int(255 * (1 - ratio))
        green = 0

        return f'#{red:02x}{green:02x}{blue:02x}'

    def Draw(wrapper: CanvasWrapper, history: HistoryData, forecast: ForecastData, config: SizeElementSettings):
        if (not config.Enabled):
            return

        x = config.X
        y = config.Y
        width = config.Width
        height = config.Height

        hourlyTemps = defaultdict(list)

        wrapper.Line(x, y, x+width, y, fillColor="white", width=2, smooth=True)
        wrapper.Line(x, y+height, x+width, y+height, fillColor="white", width=2, smooth=True)

        now = datetime.now()
        
        minTime = now.replace(minute=0,second=0,microsecond=0) - timedelta(hours=24)
        maxTime = now.replace(minute=0,second=0,microsecond=0)
        minTimestamp = now + timedelta(days=5)
        maxTimestamp = now - timedelta(days=5)
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
                wrapper.Oval(xCur - 2, yCur - 2, xCur + 2, yCur + 2, fillColor="white", outlineColor="")

                if prevValidIndex is not None:
                    xPrev, yPrev = coords[prevValidIndex]
                    avgTemp = (tempPoints[prevValidIndex] + tempPoints[i]) / 2
                    color = TemperatureGraph.GetColorForTemp(avgTemp, low, high)
                    wrapper.Line(xPrev, yPrev, xCur, yCur, fillColor=color, width=2, smooth=True)

                prevValidIndex = i
