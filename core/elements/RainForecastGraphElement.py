from datetime import datetime, timedelta

from config.SettingsEnums import PrecipitationType
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
                return h.CloudCoverPercentage / 100
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

def CalculateMinuteGradients(forecast:ForecastData, sunTimes:SunData, pixelWidth:int):
    secondsPerPixel = 86400 / pixelWidth

    startTime = datetime.now().replace()
    currentTime = startTime
    pixels = 0
    endTime = datetime.now() + timedelta(hours=24)

    nightColor = (10,15,35) # Very Dark Blue
    duskColor = (25,35,70)# Dark(ish) Blue
    nauticalTwilightColor = (60,60,90)# Much Blue, Twinge of Orange
    civilTwilightColor = (120,90,60) # Some Blue, Much Orange
    dayColor = (135,206,235) # Light Blue
    cloudGrayColor = (169, 169, 169)

    times = [
        {"Name": "Start", "Time": datetime.now().replace(hour=0,minute=0,second=0,microsecond=0), "Color": nightColor},
        {"Name": "Dawn", "Time": sunTimes.Today.Sunrise.AstronomicalTwilight - timedelta(minutes=15), "Color": duskColor},
        {"Name": "Astronomical Twilight", "Time": sunTimes.Today.Sunrise.AstronomicalTwilight, "Color": duskColor},
        {"Name": "Nautical Twilight", "Time": sunTimes.Today.Sunrise.NauticalTwilight, "Color": nauticalTwilightColor},
        {"Name": "Civil Twilight", "Time": sunTimes.Today.Sunrise.CivilTwilight, "Color": civilTwilightColor},
        {"Name": "Day", "Time": sunTimes.Today.Sunrise.Day, "Color": dayColor},
        {"Name": "Sunset", "Time": sunTimes.Today.Sunset.Start, "Color": dayColor},
        {"Name": "Civil Twilight", "Time": sunTimes.Today.Sunset.CivilTwilight, "Color": civilTwilightColor},
        {"Name": "Nautical Twilight", "Time": sunTimes.Today.Sunset.NauticalTwilight, "Color": nauticalTwilightColor},
        {"Name": "Dusk", "Time": sunTimes.Today.Sunset.AstronomicalTwilight, "Color": duskColor},
        {"Name": "Night", "Time": sunTimes.Today.Sunset.AstronomicalTwilight + timedelta(minutes=15), "Color": nightColor},
    
        {"Name": "Dawn", "Time": sunTimes.Tomorrow.Sunrise.AstronomicalTwilight - timedelta(minutes=15), "Color": duskColor},
        {"Name": "Astronomical Twilight", "Time": sunTimes.Tomorrow.Sunrise.AstronomicalTwilight, "Color": duskColor},
        {"Name": "Nautical Twilight", "Time": sunTimes.Tomorrow.Sunrise.NauticalTwilight, "Color": nauticalTwilightColor},
        {"Name": "Civil Twilight", "Time": sunTimes.Tomorrow.Sunrise.CivilTwilight, "Color": civilTwilightColor},
        {"Name": "Day", "Time": sunTimes.Tomorrow.Sunrise.Day, "Color": dayColor},
        {"Name": "Sunset", "Time": sunTimes.Tomorrow.Sunset.Start, "Color": dayColor},
        {"Name": "Civil Twilight", "Time": sunTimes.Tomorrow.Sunset.CivilTwilight, "Color": civilTwilightColor},
        {"Name": "Nautical Twilight", "Time": sunTimes.Tomorrow.Sunset.NauticalTwilight, "Color": nauticalTwilightColor},
        {"Name": "Dusk", "Time": sunTimes.Tomorrow.Sunset.AstronomicalTwilight, "Color": duskColor},
        {"Name": "Night", "Time": sunTimes.Tomorrow.Sunset.AstronomicalTwilight + timedelta(minutes=15), "Color": nightColor},

        {"Name": "End", "Time": datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(hours=48), "Color": nightColor},
    ]

    iTime = 0
    pixelTimes = []
    while (currentTime < endTime):
        currentTime = startTime + timedelta(seconds=secondsPerPixel * pixels)
        iCur = times[iTime]
        iNext = times[iTime + 1]
        if (currentTime >= iNext["Time"]):
            iTime += 1
            iCur = times[iTime]
            iNext = times[iTime + 1]
        ratio = CalculateTimeRatio(currentTime, iCur["Time"], iNext["Time"])
        color = CalculateColor(iCur["Color"], iNext["Color"], ratio)

        leftBucket = currentTime.replace(minute=0,second=0,microsecond=0)
        rightBucket = leftBucket + timedelta(hours = 1)
        leftBucketCloud = GetCloudCover(leftBucket, forecast)
        rightBucketCloud = GetCloudCover(rightBucket, forecast)
        timeBetween = CalculateTimeRatio(currentTime, leftBucket, rightBucket)
        cloudRatio = (1 - timeBetween) * leftBucketCloud + timeBetween * rightBucketCloud
        cloudColor = CalculateColor(color, cloudGrayColor, cloudRatio)
        pixelTimes.append({"Cloud": cloudColor, "Main": color})
        pixels += 1

    return pixelTimes

class RainForecastGraphElement(ElementBase):
    def __init__(self, wrapper:CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainForecast

        return self.Refresh(store,forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.RainForecast
        er = ElementRefresh.NextHour()
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
            rain_amount = hour_data.PrecipitationRain
            cloudCoverPercentage = hour_data.CloudCoverPercentage
            if rain_amount > 0:
                HasRain = True
            
            time_str = hour_data.Time
            Time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            Hour12 = Time.strftime("%I").lstrip("0")
            AMPM = Time.strftime("%p").lower()[0]
            hour_label = Hour12 + AMPM
            WeatherEmoji = WeatherHelpers.GetWeatherEmoji(hour_data.ConditionText, Time, forecast, sunData)

            bar_height = (rain_chance / max_rain) * barMaxHeight
            x = x_start + i * (barWidth + barSpacing)

            self.Wrapper.Rectangle(
                x, y_start + barMaxHeight - bar_height, x + barWidth, y_start + barMaxHeight,
                fillColor="blue", outlineColor=""
            )

            store.RainForecastGraph.HourLabels.append(self.Wrapper.TextElement(hour_label, config.Hour, xOffset = x + 2 + barWidth // 2, yOffset = y_start - 24))
            store.RainForecastGraph.WeatherEmojis.append(self.Wrapper.EmojiElement(WeatherEmoji["Emoji"], config.Emoji, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 107))
            store.RainForecastGraph.CloudCoverPercentages.append(self.Wrapper.TextElement(F"{cloudCoverPercentage}%", config.CloudCover, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 135))
            
            if rain_amount > 0:
                store.RainForecastGraph.PrecipitationAmounts.append(self.Wrapper.TextElement(f"{rain_amount}{rainAddon}", config.RainAmount, xOffset=x + 2 + barWidth // 2, yOffset=y_start - 40))

        store.TopLine = self.Wrapper.Line(x_start, y_start, x_start + ((barSpacing + barWidth) * 24), y_start, fillColor="white")
        store.BottomLine = self.Wrapper.Line(x_start, y_start + barMaxHeight, x_start + ((barSpacing + barWidth) * 24), y_start + barMaxHeight, fillColor="white")

        if not HasRain:
            store.RainForecastGraph.NoRainWarning = self.Wrapper.TextElement("No Rain Detected in the next 24 Hours", config.NoRainWarning, xOffset = x_start + ((barWidth + barSpacing) * 12), yOffset = y_start + 25)

        return er