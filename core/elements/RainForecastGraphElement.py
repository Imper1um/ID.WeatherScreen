from datetime import datetime, timedelta
import logging

from config.IconType import IconType
from config.SettingsEnums import PrecipitationType
from config.WeatherConfig import WeatherConfig
from .ElementBase import ElementBase
from .ElementRefresh import ElementRefresh
from core.drawing import CanvasWrapper
from config import WeatherSettings
from helpers import Delay, WeatherHelpers
from data import *
from core.store.WeatherDisplayStore import WeatherDisplayStore

def GetCloudCover(bucket: datetime, forecast:ForecastData) -> float:
        bucketName = bucket.strftime("%Y-%m-%d %H:%M")
        for h in forecast.Next24Hours:
            if (h.Time == bucketName):
                return h.Conditions.CloudCover
        return 0

def CalculateChannel(channel1, channel2, percent):
    return int(channel1 + (channel2 - channel1) * percent)

def CalculateColor(color1, color2, percent: float):
    r = CalculateChannel(color1[0], color2[0], percent)
    g = CalculateChannel(color1[1], color2[1], percent)
    b = CalculateChannel(color1[2], color2[2], percent)

    return (r,g,b)

def CalculateTimeRatio(currentTime: datetime, time1: datetime, time2: datetime) -> float:
    totalDuration = (time2 - time1).total_seconds()
    elapsed = (currentTime - time1).total_seconds()
    ratio = elapsed / totalDuration

    return max(0.0, min(1.0, ratio))

def CalculateMinuteGradients(forecast:ForecastData, sunData:SunData, pixelWidth:int):
    secondsPerPixel = 86400 / pixelWidth

    startTime = datetime.now().replace()
    currentTime = startTime
    endTime = datetime.now() + timedelta(hours=24)

    cloudGrayColor = (169, 169, 169)

    pixelTimes = []
    while (currentTime < endTime):
        currentTime = currentTime + timedelta(seconds=secondsPerPixel)

        baseColorHex = sunData.GetSkyColor(currentTime)
        baseColor = tuple(int(baseColorHex[j:j+2], 16) for j in (1, 3, 5))

        leftBucket = currentTime.replace(minute=0, second=0, microsecond=0)
        rightBucket = leftBucket + timedelta(hours=1)
        leftCloud = GetCloudCover(leftBucket, forecast)
        rightCloud = GetCloudCover(rightBucket, forecast)
        timeRatio = CalculateTimeRatio(currentTime, leftBucket, rightBucket)
        cloudRatio = (1 - timeRatio) * leftCloud + timeRatio * rightCloud

        cloudColor = CalculateColor(baseColor, cloudGrayColor, cloudRatio)
        pixelTimes.append({"Cloud": cloudColor, "Main": baseColor})

    return pixelTimes

class RainForecastGraphElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, config: WeatherConfig):
        self.Wrapper = wrapper
        self.Config = config
        self.Settings = config.Weather

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainForecast

        return self.Refresh(store,forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainForecast
        er = ElementRefresh.NextHour()
        er.Delay += 60 * 1000
        er.Reasons = [ElementRefresh.OnTimer, ElementRefresh.OnUpdateForecastData]
        if (not config.Enabled):
            return er

        if (not forecast.Next24Hours or len(forecast.Next24Hours) < 1):
            return er

        store.RainForecastGraph.Clear()

        HasRain = False

        barWidth = config.BarWidth
        barSpacing = config.BarSpacing
        barMaxHeight = config.BarMaxHeight
        x_start = config.X
        y_start = config.Y
        rainAddon = '"' if self.Settings.Precipitation == PrecipitationType.IN else 'mm'

        if (config.SkyGradient.Enable):
            gradientWidth = (barWidth + barSpacing) * 24
            secondsPerPixel = 86400 / gradientWidth
            er.Delay = int(secondsPerPixel * 1000)
            colorPixels = CalculateMinuteGradients(forecast, sunData, gradientWidth)
            now = datetime.now()
            gradientHeight = 35
            secondsPastHour = now.minute * 60 + now.second

            firstHour = datetime.strptime(forecast.Next24Hours[0].Time, "%Y-%m-%d %H:%M")
            currentHour = now.replace(minute=0,second=0,microsecond=0)

            if (firstHour < currentHour):
                secondsPastHour += 60 * 60

            pushRight = int(secondsPastHour / secondsPerPixel) + x_start
            i = 0
            cloudHeight = config.SkyGradient.CloudHeight if config.SkyGradient.EnableCloud else 0
            for pixel in colorPixels:
                if (pushRight + i > gradientWidth + barSpacing):
                    continue
                fillColor = f"#{pixel['Main'][0]:02x}{pixel['Main'][1]:02x}{pixel['Main'][2]:02x}"
                cloudFillColor = f"#{pixel['Cloud'][0]:02x}{pixel['Cloud'][1]:02x}{pixel['Cloud'][2]:02x}"

                if (config.SkyGradient.EnableCloud):
                    store.RainForecastGraph.CloudGradientLines.append(self.Wrapper.Line(pushRight + i, y_start + barMaxHeight, pushRight + i, y_start + barMaxHeight + cloudHeight, fillColor=cloudFillColor))
                
                store.RainForecastGraph.AmbientLightLines.append(self.Wrapper.Line(pushRight + i, y_start + barMaxHeight + cloudHeight, pushRight + i, y_start + barMaxHeight + gradientHeight, fillColor=fillColor))
                i += 1

        max_rain = 100  # Max rain chance is 100%
        for i, hour_data in enumerate(forecast.Next24Hours[:24]):
            rain_chance = hour_data.RainChance
            rain_amount = hour_data.Conditions.RainRate
            cloudCoverPercentage = int(hour_data.Conditions.CloudCover * 100)
            if rain_amount > 0:
                HasRain = True
            
            time_str = hour_data.Time
            Time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            WeatherEmoji = hour_data.Conditions.GetEmoji()
            WeatherIcon = hour_data.Conditions.GetIcon()

            bar_height = (rain_chance / max_rain) * barMaxHeight
            x = x_start + i * (barWidth + barSpacing)

            store.RainForecastGraph.PrecipitationChances.append(self.Wrapper.Rectangle(
                x, y_start + barMaxHeight - bar_height, x + barWidth, y_start + barMaxHeight,
                fillColor="blue", outlineColor=""
            ))


            store.RainForecastGraph.HourLabels.append(self.Wrapper.FormattedTextElement(Time, config.Hour, xOffset = x + 2 + barWidth // 2, yOffset = y_start - 24))
            weatherEmoji = self.Wrapper.StackedEmojiElement(WeatherEmoji, config.Emoji, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 107)
            if weatherEmoji is not None:
                store.RainForecastGraph.WeatherEmojis.append(weatherEmoji)
            if (WeatherIcon.Icon != IconType.Unknown):
                basePath = self.Config._basePath
                folder = "/assets/icons/"
                stoke = "-Outline" if self.Settings.CurrentTempIcon.Stroke else ""
                icon = F'Icon-{WeatherIcon.Icon.value}{stoke}.png'
                path = F'{basePath}{folder}{icon}'
                weatherIcon = self.Wrapper.StackedIconElement(path, WeatherIcon, config.Icon, xOffset=x-5, yOffset=y_start + 100)
                if weatherIcon is not None:
                    store.RainForecastGraph.WeatherIcons.append(weatherIcon)
            store.RainForecastGraph.CloudCoverPercentages.append(self.Wrapper.TextElement(F"{cloudCoverPercentage}%", config.CloudCover, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 135))
            
            if rain_amount > 0:
                store.RainForecastGraph.PrecipitationAmounts.append(self.Wrapper.TextElement(f"{rain_amount}{rainAddon}", config.RainAmount, xOffset=x + 2 + barWidth // 2, yOffset=y_start - 40))

        store.TopLine = self.Wrapper.Line(x_start, y_start, x_start + ((barSpacing + barWidth) * 24), y_start, fillColor="white")
        store.BottomLine = self.Wrapper.Line(x_start, y_start + barMaxHeight, x_start + ((barSpacing + barWidth) * 24), y_start + barMaxHeight, fillColor="white")

        if not HasRain:
            store.RainForecastGraph.NoRainWarning = self.Wrapper.TextElement("No Rain Detected in the next 24 Hours", config.NoRainWarning, xOffset = x_start + ((barWidth + barSpacing) * 12), yOffset = y_start + 25)

        return er