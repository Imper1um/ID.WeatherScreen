import json, logging, math, os, platform, random
import exiftool

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dateutil import tz
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk

from config.FormattedTextElementSettings import FormattedTextElementSettings
from config.SettingsEnums import *
from config.TextElementSettings import TextElementSettings
from config.WeatherConfig import WeatherConfig

from services.WeatherService import WeatherService

from data.CurrentData import CurrentData
from data.ForecastData import ForecastData, MoonPhase
from data.HistoryData import HistoryData, HistoryLine
from data.SunData import SunData

class WeatherDisplay:
    def __init__(self, root, weatherService: WeatherService, weatherConfig: WeatherConfig):
        self.Config = weatherConfig
        self.Log = logging.getLogger("WeatherDisplay")
        self.BasePath = Path(__file__).resolve().parent
        self.Log.debug(F"BasePath: {self.BasePath}")
        self.EmojiFont = "Segoe UI Emoji"
        if (self.IsRaspberryPi()):
            self.EmojiFont = "Noto Color Emoji"
        self.Root = root
        self.FirstTry = True
        self.WeatherService = weatherService
        self.CurrentData: Optional[CurrentData] = None
        self.ForecastData: Optional[ForecastData] = None
        self.HistoryData: Optional[HistoryData] = None
        self.SunData: Optional[SunData] = None
        self.LastBackgroundImageType = None
        self.LastBackgroundImageTags = None
        self.LastBackgroundImageChange = None

        if self.IsRaspberryPi():
            self.Root.overrideredirect(True)
            self.Root.attributes('-fullscreen', True)
            self.Root.attributes('-type', "splash")
        else:
            self.Root.geometry("1920x1080")

        self.Root.title("Weather Display")
        self.current_labels = {}
        self.forecast_labels = {}
        self.canvas = tk.Canvas(self.Root, width=1920, height=1080, bg="#0f0", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.Begin = datetime.now()
        self.ThisImageTags = None
        self.ImageTagMessage = None

        self.CheckBackgroundImages()
    def CheckBackgroundImages(self):
        allBackgroundImages = self.GetAllBackgroundImages()
        self.Log.info(F"{len(allBackgroundImages)} images found.")
        allStates = ['Sunrise','Sunset','Night','Daylight']
        allConditions = ['Clear','PartlyCloudy','Cloudy','Overcast','Foggy','Lightning','LightRain','MediumRain','HeavyRain','Snow']

        for s in allStates:
            for c in allConditions:
                checkTags = [s,c]
                MatchingImages = [
                    img for img in allBackgroundImages
                    if (all(tag in img["Tags"] for tag in checkTags))]
                if not MatchingImages:
                    self.Log.warn(F'No image matches tags ["{s}","{c}"]')

    def IsRaspberryPi(self):
        uname = platform.uname()
        self.Log.debug(F"IsRaspberryPi: {platform.system()} == 'Linux' and '{uname.machine}'.startswith('aarch') == {uname.machine.startswith('aarch')}")
        return platform.system() == "Linux" and uname.machine.startswith("aarch")

    def GetUptimeString(self) -> str:
        delta = datetime.now() - self.Begin
        totalSeconds = int(delta.total_seconds())

        days = totalSeconds // 86400
        hours = (totalSeconds % 86400) // 3600
        minutes = (totalSeconds % 3600) // 60
        seconds = totalSeconds % 60

        parts = []
        if (days > 0):
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        return ' '.join(parts)

    def FormattedText(self, date: datetime, settings: FormattedTextElementSettings):
        if (not settings.Enabled):
            return
        f = settings.Format
        if "%-I" in f:
            hour = date.hour
            if (hour > 12):
                hour -= 12
            if (hour == 0):
                hour = 12
            f = f.replace("%-I", str(hour))

        self.Text(date.strftime(f), settings)
    
    def Text(self, text: str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        fontFamily = "Arial"
        if (settings.FontFamily):
            fontFamily = settings.FontFamily
        fontSize = 12
        if (settings.FontSize):
            fontSize = settings.FontSize
        fontWeight = "normal"
        if (settings.FontWeight):
            fontWeight = settings.FontWeight
        font = (fontFamily, fontSize, fontWeight)
        anchor = "nw"
        if (settings.Anchor):
            anchor = settings.Anchor

        if (settings.Stroke):
            s = {
                "anchor": anchor,
                "mainFill": settings.FillColor
            }
            s = {k: v for k, v in s.items() if v is not None}
            self.CreateTextWithStroke(text, font, settings.X + xOffset, settings.Y + yOffset, **s)
        else:
            s = {
                "fill": settings.FillColor,
                "font": font,
                "anchor": anchor
            }
            s = {k: v for k, v in s.items() if v is not None}
            self.canvas.create_text(settings.X + xOffset, settings.Y + yOffset, text=text, **s)

    def EmojiText(self, text: str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        fontFamily = self.EmojiFont
        fontSize = 12
        if (settings.FontSize):
            fontSize = settings.FontSize
        fontWeight = "normal"
        if (settings.FontWeight):
            fontWeight = settings.FontWeight
        font = (fontFamily, fontSize, fontWeight)
        anchor = "nw"
        if (settings.Anchor):
            anchor = settings.Anchor

        s = {
            "fill": settings.FillColor,
            "font": font,
            "anchor": anchor
        }
        s = {k: v for k, v in s.items() if v is not None}
        self.canvas.create_text(settings.X + xOffset, settings.Y + yOffset, text=text, **s)

        

    def RefreshScreen(self):
        now = datetime.now()
        DayOfWeek = now.strftime("%A")

        self.CurrentFrame = ttk.LabelFrame(self.Root, text="Weather Test")
       
        self.canvas.delete("all")
        self.LoadBackgroundImage()
        self.Text(DayOfWeek, self.Config.Weather.DayOfWeek)
        self.FormattedText(now, self.Config.Weather.FullDate)
        self.FormattedText(now, self.Config.Weather.Time)
        self.Text(F"Uptime: {self.GetUptimeString()}", self.Config.Weather.Uptime)
        self.FormattedText(self.CurrentData.LastUpdate, self.Config.Weather.LastUpdated)
        self.FormattedText(self.CurrentData.ObservedTimeLocal, self.Config.Weather.Observed)
        self.Text(F"Source: {self.CurrentData.Source}", self.Config.Weather.Source)
        imageTags = F"Requested Image Tags: {self.LastBackgroundImageTags} // This Image Tags: {self.ThisImageTags}"
        if (self.ImageTagMessage):
            imageTags += F" // Image Message: {self.ImageTagMessage}"

        self.Text(imageTags, self.Config.Weather.ImageTags)

        if (self.CurrentData.Source == "Station"):
            station = F"Station: {self.CurrentData.StationId}"
            self.Text(station, self.Config.Weather.Station)

        try:
            temp = self.CurrentData.CurrentTemp
            feelsLikeTemp = self.CurrentData.FeelsLike
            feelsLike = f"Feels Like: {feelsLikeTemp}°"
            state = self.CurrentData.State
            emoji = self.GetWeatherEmoji(state, now)
            display = f"{temp}°"
            self.Text(display, self.Config.Weather.CurrentTemp)
            self.Text(feelsLike, self.Config.Weather.FeelsLike)
            self.EmojiText(emoji["Emoji"], self.Config.Weather.CurrentTempEmoji)
            self.Text(self.ForecastData.Daytime.High, self.Config.Weather.TempHigh)
            self.Text(self.ForecastData.Nighttime.Low, self.Config.Weather.TempLow)
        except Exception as e:
            self.Log.warn(f"Failed to render weather info: {e}")

        self.DrawWindIndicator()
        self.DrawRainForecastGraph()
        self.DrawRainSquare()
        self.DrawTemperatureGraph()
        self.DrawHumiditySquare()

        self.Root.after(1000, self.RefreshScreen)

    def DrawTemperatureGraph(self):
        config = self.Config.Weather.TemperatureGraph
        if (not config.Enabled):
            return

        x = config.X
        y = config.Y
        width = config.Width
        height = config.Height

        hourlyTemps = defaultdict(list)
        history = self.HistoryData

        self.canvas.create_line(x, y, x+width, y, fill="white", width=2, smooth=True)
        self.canvas.create_line(x, y+height, x+width, y+height, fill="white", width=2, smooth=True)
        

        now = datetime.now()
        
        minTime = now.replace(minute=0,second=0,microsecond=0) - timedelta(hours=24)
        maxTime = now.replace(minute=0,second=0,microsecond=0)
        minTimestamp = now + timedelta(days=5)
        maxTimestamp = now - timedelta(days=5)
        high = self.ForecastData.Daytime.High
        low = self.ForecastData.Nighttime.Low
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
                self.canvas.create_oval(xCur - 2, yCur - 2, xCur + 2, yCur + 2, fill="white", outline="")

                if prevValidIndex is not None:
                    xPrev, yPrev = coords[prevValidIndex]
                    avgTemp = (tempPoints[prevValidIndex] + tempPoints[i]) / 2
                    color = self.GetColorForTemp(avgTemp, low, high)
                    self.canvas.create_line(xPrev, yPrev, xCur, yCur, fill=color, width=2, smooth=True)

                prevValidIndex = i

        self.FirstTry = False

    def GetColorForTemp(self, temp, low, high):
        ratio = (temp - low) / max(high - low, 1)
        ratio = max(0.0, min(1.0, ratio))

        red = int(255 * ratio)
        blue = int(255 * (1 - ratio))
        green = 0

        return f'#{red:02x}{green:02x}{blue:02x}'

    def DrawHumiditySquare(self):
        if (not self.CurrentData or not self.CurrentData.Humidity):
            return

        try:
            humidity = self.CurrentData.Humidity
            config = self.Config.Weather.HumiditySquare
            if (not config.Enabled):
                return
            x = config.X
            y = config.Y
            size = config.Size

            fill_ratio = humidity / 100
            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height
            self.canvas.create_rectangle(x + 1, top_fill_y, x + size - 2, y + size - 2, fill="#00BFFF",outline=None)
            self.canvas.create_rectangle(x, y, x + size, y + size, outline="white", width=2)
            self.EmojiText("💦", config.Emoji, xOffset =  x + size // 2, yOffset = y + size // 2)
            label = f"{humidity}%"
            self.Text(label, config.Text, xOffset = x + size // 2, yOffset = y + size // 2)
        except Exception as e:
            self.Log.warn(f"Failed to draw humidity square: {e}")

    def DrawRainSquare(self):
        if (not self.CurrentData or not self.CurrentData.Rain):
            return

        try:
            config = self.Config.Weather.RainSquare
            if (not config.Enabled):
                return
            max_inches = config.MaxRain
            size = config.Size
            x = config.X
            y = config.Y

            rain_inches = self.CurrentData.Rain
            max_inches = config.MaxRain
            rain_inches = min(max(rain_inches, 0), max_inches)
            fill_ratio = rain_inches / max_inches

            rainAddon = '"' if self.Config.Weather.Precipitation == PrecipitationType.IN else 'MM'

            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height

            self.canvas.create_rectangle(x, top_fill_y, x + size, y + size, fill="blue", outline="blue")
            self.canvas.create_rectangle(x, y, x + size, y + size, outline="white", width=2)
            self.EmojiText("💧", config.Emoji, xOffset=x + size // 2, yOffset= y + size // 2)
            label = f"{rain_inches:.2f}{rainAddon}"
            self.Text(label, config.Text, xOffset=x + size // 2, yOffset=y + size // 2)
        except Exception as e:
            self.Log.warn(f"Failed to draw rain square: {e}")

    def DrawRainForecastGraph(self):
        forecast = self.ForecastData.Next24Hours
        if not forecast:
            return

        config = self.Config.Weather.RainForecast
        if (not config.Enabled):
            return

        HasRain = False

        barWidth = config.BarWidth
        barSpacing = config.BarSpacing
        barMaxHeight = config.BarMaxHeight
        x_start = config.X
        y_start = config.Y
        rainAddon = '"' if self.Config.Weather.Precipitation == PrecipitationType.IN else 'mm'

        if (config.SkyGradient.Enable):
            gradientWidth = (barWidth + barSpacing) * 24
            secondsPerPixel = 86400 / gradientWidth
            colorPixels = self.CalculateMinuteGradients(gradientWidth)
            now = datetime.now()
            gradientHeight = 35
            secondsPastHour = now.minute * 60 + now.second

            firstHour = datetime.strptime(forecast[0].Time, "%Y-%m-%d %H:%M")
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
                    self.canvas.create_line(pushRight + i, y_start + barMaxHeight, pushRight + i, y_start + barMaxHeight + cloudHeight, fill=cloudFillColor)
                self.canvas.create_line(pushRight + i, y_start + barMaxHeight + cloudHeight, pushRight + i, y_start + barMaxHeight + gradientHeight, fill=fillColor)
                i += 1

        max_rain = 100  # Max rain chance is 100%
        for i, hour_data in enumerate(forecast[:24]):
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
            WeatherEmoji = self.GetWeatherEmoji(hour_data.ConditionText, Time)

            bar_height = (rain_chance / max_rain) * barMaxHeight
            x = x_start + i * (barWidth + barSpacing)

            self.canvas.create_rectangle(
                x, y_start + barMaxHeight - bar_height, x + barWidth, y_start + barMaxHeight,
                fill="blue", outline=""
            )

            self.Text(hour_label, config.Hour, xOffset = x + 2 + barWidth // 2, yOffset = y_start - 24)
            self.EmojiText(WeatherEmoji["Emoji"], config.Emoji, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 107)
            self.Text(F"{cloudCoverPercentage}%", config.CloudCover, xOffset=x + 2 + barWidth // 2, yOffset=y_start + 135)
            
            if rain_amount > 0:
                self.Text(f"{rain_amount}{rainAddon}", config.RainAmount, xOffset=x + 2 + barWidth // 2, yOffset=y_start - 40)

        self.canvas.create_line(x_start, y_start, x_start + ((barSpacing + barWidth) * 24), y_start, fill="white")
        self.canvas.create_line(x_start, y_start + barMaxHeight, x_start + ((barSpacing + barWidth) * 24), y_start + barMaxHeight, fill="white")

        if not HasRain:
            self.Text("No Rain Detected in the next 24 Hours", config.NoRainWarning, xOffset = x_start + ((barWidth + barSpacing) * 12), yOffset = y_start + 25)

    def ToLocalNaive(self, iso_string: str) -> datetime:
        utc = datetime.fromisoformat(iso_string)
        local = utc.astimezone(tz.tzlocal()).replace(tzinfo=None)
        return local

    def CalculateMinuteGradients(self, pixelWidth):
        forecast = self.ForecastData
        sunTimes = self.SunData
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
            ratio = self.CalculateTimeRatio(currentTime, iCur["Time"], iNext["Time"])
            color = self.CalculateColor(iCur["Color"], iNext["Color"], ratio)

            leftBucket = currentTime.replace(minute=0,second=0,microsecond=0)
            rightBucket = leftBucket + timedelta(hours = 1)
            leftBucketCloud = self.GetCloudCover(leftBucket)
            rightBucketCloud = self.GetCloudCover(rightBucket)
            timeBetween = self.CalculateTimeRatio(currentTime, leftBucket, rightBucket)
            cloudRatio = (1 - timeBetween) * leftBucketCloud + timeBetween * rightBucketCloud
            cloudColor = self.CalculateColor(color, cloudGrayColor, cloudRatio)
            pixelTimes.append({"Cloud": cloudColor, "Main": color})
            pixels += 1

        return pixelTimes

    

    def GetCloudCover(self, bucket: datetime) -> float:
        bucketName = bucket.strftime("%Y-%m-%d %H:%M")
        for h in self.ForecastData.Next24Hours:
            if (h.Time == bucketName):
                return h.CloudCoverPercentage / 100
        return 0

    def CalculateTimeRatio(self, currentTime: datetime, time1: datetime, time2: datetime) -> float:
        totalDuration = (time2 - time1).total_seconds()
        elapsed = (currentTime - time1).total_seconds()
        ratio = elapsed / totalDuration

        return max(0.0, min(1.0, ratio))

        
    def CalculateColor(self, color1, color2, percent: float):
        r = self.CalculateChannel(color1[0], color2[0], percent)
        g = self.CalculateChannel(color1[1], color2[1], percent)
        b = self.CalculateChannel(color1[2], color2[2], percent)

        return (r,g,b)

    def CalculateChannel(self, channel1, channel2, percent):
        return int(channel1 + (channel2 - channel1) * percent)

    def DrawWindIndicator(self):
        config = self.Config.Weather.WindIndicator
        radius = config.Size
        x = config.X
        y = config.Y

        wind = self.CurrentData.WindSpeed
        gust = self.CurrentData.WindGust
        direction = self.CurrentData.WindDirection
        addon = "MPH" if self.Config.Weather.Wind == WindType.MPH else "KPH"

        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="white", width=3)
        font = ("Arial", 22, "bold")
        degreeFont = ("Arial", 18)

        speed_text = f"{wind:.1f} {addon}"
        gust_text = f"({gust:.1f} {addon})"

        angle_rad = math.radians(direction - 90)
        end_x = x + math.cos(angle_rad) * radius * 1.2
        end_y = y + math.sin(angle_rad) * radius * 1.2

        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = int((direction + 11.25) % 360 / 22.5)
        compass = directions[index]
        degree_label = f"{direction:.0f}° ({compass})"

        historyArrows = config.HistoryArrows
        pastLines = [
            line for line in reversed(self.HistoryData.Lines[:-1])
            if hasattr(line, "WindDirection")
            ][:historyArrows]
        for i, line in enumerate(reversed(pastLines)):
            pastDirection = line.WindDirection
            fade = 0.1 + (0.5 * (i + 1) / historyArrows)
            grayValue = int(255 * fade)
            gray = f"#{grayValue:02x}{grayValue:02x}{grayValue:02x}"

            angleRad = math.radians(pastDirection - 90)
            fadedX = x + math.cos(angleRad) * radius * 0.95
            fadedY = y + math.sin(angleRad) * radius * 0.95
            self.canvas.create_line(x, y, fadedX, fadedY, fill=gray, width=3, arrow=tk.LAST)

        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            self.canvas.create_line(x + dx, y + dy, end_x + dx, end_y + dy, fill="black", width=5, arrow=tk.LAST)

        self.canvas.create_line(x, y, end_x, end_y, fill="white", width=5, arrow=tk.LAST)
        self.Text(speed_text, config.Wind, xOffset=x, yOffset= y - 30)
        self.Text(gust_text, config.Gust, xOffset=x, yOffset=y)
        self.Text(degree_label, config.Direction, xOffset=x, yOffset=y + 30)

    def GetWeatherEmoji(self, state, time):
        text = state.lower()
        Moon = self.ForecastData.Moon
        IsNight = self.IsNight(time)
        IsSunset = self.IsSunset(time)
        IsSunrise = self.IsSunrise(time)

        if "thunder" in text:
            return {"Emoji": "⛈️", "Color": "#FFD700"}  # Gold
        if "rain" in text or "shower" in text or "drizzle" in text:
            return {"Emoji": "🌧️", "Color": "#1E90FF"}  # Dodger Blue
        if IsNight and Moon == MoonPhase.NewMoon:
            return {"Emoji": Moon.ToEmoji, "Color": "#222222"}  # Dark gray
        if IsNight and Moon == MoonPhase.FullMoon:
            return {"Emoji": Moon.ToEmoji, "Color": "#FFFFE0"}  # Light Yellow
        if IsNight and Moon == MoonPhase.WaxingCrescent:
            return {"Emoji": Moon.ToEmoji, "Color": "#CCCCCC"}
        if IsNight and Moon == MoonPhase.FirstQuarter:
            return {"Emoji": Moon.ToEmoji, "Color": "#DDDDDD"}
        if IsNight and Moon == MoonPhase.WaxingGibbous:
            return {"Emoji": Moon.ToEmoji, "Color": "#EEEEEE"}
        if IsNight and Moon == MoonPhase.WaningGibbous:
            return {"Emoji": Moon.ToEmoji, "Color": "#EEEEEE"}
        if IsNight and Moon == MoonPhase.LastQuarter:
            return {"Emoji": Moon.ToEmoji, "Color": "#DDDDDD"}
        if IsNight and Moon == MoonPhase.WaningCrescent:
            return {"Emoji": Moon.ToEmoji, "Color": "#CCCCCC"}
        if "sun" in text and "cloud" in text:
            return {"Emoji": "⛅", "Color": "#FFE066"}  # Light Yellow/Cloud mix
        if "partly" in text:
            return {"Emoji": "🌤️", "Color": "#FFD966"}  # Warm sunny
        if "sun" in text or "clear":
            return {"Emoji": "☀️", "Color": "#FFA500"}  # Orange
        if "cloud" in text or "overcast" in text:
            return {"Emoji": "☁️", "Color": "#B0C4DE"}  # LightSteelBlue
        if "snow" in text:
            return {"Emoji": "🌨️", "Color": "#ADD8E6"}  # Light Blue
        if "fog" in text or "mist" in text:
            return {"Emoji": "🌫️", "Color": "#C0C0C0"}  # Silver
        if IsSunrise:
            return {"Emoji": "🌅", "Color": "#FFA07A"}  # Light Salmon
        if IsSunset:
            return {"Emoji": "🌆", "Color": "#FF7F50"}  # Coral

        self.Log.debug(f"Could not parse '{state}' at '{time}' into a weather Emoji. Night: {IsNight}, Sunrise: {IsSunrise}, Sunset: {IsSunset}")
        return {"Emoji": "❓", "Color": "#FFFFFF"}  # Fallback to white

    def GetAllBackgroundImages(self):
        image_dir = os.path.join(self.BasePath, "assets", "backgrounds")
        self.Log.debug(F"image_dir: {image_dir}")
        if not os.path.exists(image_dir):
            self.Log.warn(f"Background directory does not exist: {image_dir}")
            return []

        image_data = []
        image_files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.lower().endswith(".jpg") or f.lower().endswith(".png")
        ]

        if not image_files:
            return []

        with exiftool.ExifTool() as et:
            args = ["-IPTC:Keywords", "-XMP:Subject", "-json"] + image_files
            raw_output = et.execute(*args)  # already returns a str

            metadata_list = json.loads(raw_output)

            for meta in metadata_list:
                path = meta.get("SourceFile")
                keywords = meta.get("IPTC:Keywords") or meta.get("XMP:Subject") or []

                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(";")]

                image_data.append({
                    "Path": path,
                    "Tags": keywords
                })

        return image_data


    def LoadBackgroundImage(self):
        img = Image.open(self.LastBackgroundImagePath)
        img = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.Resampling.LANCZOS)
        self.BackgroundImage = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.BackgroundImage, anchor="nw")

    def ChangeBackgroundImage(self):
        now = datetime.now()
        current_tags = self.GetWeatherTags(now)

        ShouldChange = False
        if (self.LastBackgroundImageTags is None or set(current_tags) != set(self.LastBackgroundImageTags)):
            ShouldChange = True
        if self.LastBackgroundImageChange is None or now - self.LastBackgroundImageChange >= timedelta(minutes=10):
            ShouldChange = True

        if not ShouldChange:
            return

        self.LastBackgroundImageChange = now
        self.LastBackgroundImageTags = current_tags
        
        AllImages = self.GetAllBackgroundImages()
        MatchingImages = [
            img for img in AllImages
            if (all(tag in img["Tags"] for tag in current_tags))
        ]

        self.ImageTagMessage = ""

        if not MatchingImages:
            SelectedFile = random.choice(AllImages)
            self.ImageTagMessage = "Could not find Matching Image"
        else:
            SelectedFile = random.choice(MatchingImages)

        self.ThisImageTags = SelectedFile["Tags"]
        self.LastBackgroundImagePath = SelectedFile["Path"]

    def GetWeatherTags(self, time):
        state = self.CurrentData.State.lower()
        tags = []

        if self.IsSunrise(time):
            tags.append("Sunrise")
        elif self.IsSunset(time):
            tags.append("Sunset")
        elif self.IsNight(time):
            tags.append("Night")
        else:
            tags.append("Daylight")

        condition_map = {
            "sunny": "Clear",
            "clear": "Clear",
            "partly cloudy": "PartlyCloudy",
            "cloudy": "Cloudy",
            "overcast": "Overcast",
            "mist": "Foggy",
            "fog": "Foggy",
            "freezing fog": "Foggy",
            "thundery": "Lightning",
            "thunder": "Lightning",
            "light drizzle": "LightRain",
            "patchy light drizzle": "LightRain",
            "patchy rain": "LightRain",
            "patchy light rain": "LightRain",
            "light rain": "LightRain",
            "moderate rain": "MediumRain",
            "moderate rain at times": "MediumRain",
            "heavy rain": "HeavyRain",
            "heavy rain at times": "HeavyRain",
            "torrential rain": "HeavyRain",
            "blizzard": "Snow",
            "snow": "Snow",
            "patchy snow": "Snow",
            "ice": "Snow",
            "hail": "Snow",
            "sleet": "Snow",
            "freezing drizzle": "LightRain",
            "freezing rain": "MediumRain",
        }

        # Match condition text
        for key, tag in condition_map.items():
            if key in state:
                tags.append(tag)
                break
        else:
            # fallback if unknown
            tags.append("Unknown")

        return tags


    def StartDataRefresh(self):
        self.GrabHistoricalData();
        self.RefreshCurrentData();
        self.RefreshSunData();
        self.RefreshForecastData();
        self.ChangeBackgroundImage()
        self.RefreshScreen();
        

        if (self.IsRaspberryPi()):
            self.Root.after(2000, self.EnsureFullscreen)

    def EnsureFullscreen(self):
        width = self.Root.winfo_width()
        height = self.Root.winfo_height()
        screen_width = self.Root.winfo_screenwidth()
        screen_height = self.Root.winfo_screenheight()

        if (width < screen_width or height < screen_height):
            self.Log.warning(F"Window is not fullscreen... attempting fullscreen push")
            self.Root.attributes("-fullscreen", True)

    def DebugBuckets(self, reason):
        if (not self.Config.Logging.EnableTrace):
            return

        hourlyTemps = defaultdict(list)
        for timestamp, data in self.HistoryData:
            utcTimestamp = timestamp.astimezone(timezone.utc)
            if "CurrentTempF" in data:
                hourBucket = utcTimestamp.replace(minute=0, second=0, microsecond=0)
                hourlyTemps[hourBucket].append(data["CurrentTempF"])
        
        hourBuckets = hourlyTemps.keys()
        self.Log.debug(F"{reason}: hourBuckets = {hourBuckets} ({len(hourBuckets)})")

    def GrabHistoricalData(self):
        historicalData = self.WeatherService.GetHistoryData();
        self.HistoryData = historicalData
        self.DebugBuckets("GrabHistoricalData");

    def RefreshSunData(self):
        now = datetime.now()
        self.SunData = self.WeatherService.GetSunData(self.CurrentData.Latitude, self.CurrentData.Longitude, now);

        tomorrow = (now + timedelta(days = 1)).replace(hour = 0, minute = 0, second = 5, microsecond = 0)
        delay = (tomorrow - now).total_seconds() * 1000
        self.Root.after(int(delay), self.RefreshSunData)

    def AppendToHistory(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cutoff = now - timedelta(hours=26)
        currentData = self.CurrentData;

        self.DebugBuckets("RefreshStationdata Pre-Append")
        self.HistoryData.Lines.append(currentData)
        self.DebugBuckets("RefreshStationdata Post-Append")
        newHistory = []
        for line in self.HistoryData.Lines:
            timestamp = line.ObservedTimeUtc.replace(tzinfo=None)
            if (timestamp >= cutoff):
                newHistory.append(line)

        self.HistoryData.Lines = newHistory
        self.DebugBuckets("RefreshStationdata Post-Filter")

    def RefreshCurrentData(self):
        currentData = self.WeatherService.GetCurrentData()
        self.CurrentData = currentData;
        self.AppendToHistory()

        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"RefreshCurrentData: {currentData}")
        if (self.SunData):
            self.ChangeBackgroundImage()

        self.Root.after(60 * 1000, self.RefreshCurrentData)

    def ClassifyWeatherBackground(self):
        condition = self.CurrentData.get("State", "").lower()
        now = datetime.now().astimezone()
        is_night = self.IsNight(now)

        try:
            if self.IsSunrise(now):
                return "Sunrise"
            elif self.IsSunset(now):
                return "Sunset"
            elif self.IsNight(now):
                return "Night"

        except Exception as e:
            self.Log.warn(f"Failed to classify sunrise/sunset window: {e}")

        # Weather-based conditions (fallbacks)
        if "rain" in condition or "shower" in condition:
            return "Rainy"
        if "sunny" in condition and not is_night:
            return "Sunny"
        if "partly" in condition or "mostly sunny" in condition:
            return "PartlyCloudy"
        if "cloud" in condition or "overcast" in condition:
            return "Cloudy"
        if is_night:
            return "Night"

        return "Cloudy"

    def IsNight(self, time):
        try:
            
            sunriseToday = self.SunData.Today.Sunrise.AstronomicalTwilight
            sunsetToday = self.SunData.Today.Sunset.AstronomicalTwilight

            sunriseTomorrow = self.SunData.Tomorrow.Sunrise.AstronomicalTwilight
            sunsetTomorrow = self.SunData.Tomorrow.Sunset.AstronomicalTwilight

            return time < sunriseToday or sunsetToday < time < sunriseTomorrow or sunsetTomorrow < time
        except Exception as e:
            self.Log.warn(f"is_night exception: {e}")
            return False

    def IsSunset(self, time):
        try:


            start = self.SunData.Today.Sunset.Start
            end = self.SunData.Today.Sunset.AstronomicalTwilight

            tomorrowstart = self.SunData.Tomorrow.Sunset.Start
            tomorrowend = self.SunData.Today.Sunset.AstronomicalTwilight

            if (self.Config.Logging.EnableTrace):
                self.Log.debug(F"Sunset: {start} < {time} < {end} = {start < time < end} or {tomorrowstart} <= {time} <= {tomorrowend} = {tomorrowstart <= time <= tomorrowend}")

            return start <= time <= end or tomorrowstart <= time <= tomorrowend

        except Exception as e:
            self.Log.warn(f"Failed to determine sunset time: {e}")
            return False

    def IsSunrise(self, time):
        try:
            start = self.SunData.Today.Sunrise.AstronomicalTwilight
            end = self.SunData.Today.Sunrise.Day

            tomorrowstart = self.SunData.Tomorrow.Sunrise.AstronomicalTwilight
            tomorrowend = self.SunData.Tomorrow.Sunrise.Day
            return start <= time <= end or tomorrowstart <= time <= tomorrowend
        except:
            return False


    def RefreshForecastData(self):
        self.ForecastData = self.WeatherService.GetForecastData()
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"RefreshForecastData: {self.ForecastData}")
            self.Log.debug("----")

        self.Root.after(60 * 60 * 1000, self.RefreshForecastData)
            
    def CreateTextWithStroke(self, text, font, x, y, anchor = "nw", mainFill="white"):
        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            self.canvas.create_text(x + dx, y + dy, text=text, font=font, fill="black", anchor=anchor)

        self.canvas.create_text(x, y, text=text, font=font, fill=mainFill, anchor=anchor)
