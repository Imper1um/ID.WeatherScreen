import json
import exiftool
import logging
import math
import os
import platform
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, timezone
from dateutil import tz
from PIL import Image, ImageTk
from pathlib import Path
from collections import defaultdict

class WeatherDisplay:
    def __init__(self, root, weatherService, weatherEncoder):
        self.EnableTrace = os.getenv("ENABLE_TRACE", "No") == "Yes"
        self.EnableImageTagDisplay = os.getenv("ENABLE_IMAGETAGS", "No") == "Yes"
        self.Log = logging.getLogger("WeatherDisplay")
        self.BasePath = Path(__file__).resolve().parent
        self.Log.info(F"BasePath: {self.BasePath}")
        self.EmojiFont = "Segoe UI Emoji"
        if (self.IsRaspberryPi()):
            self.EmojiFont = "Noto Color Emoji"
        self.Root = root
        self.FirstTry = True
        self.WeatherService = weatherService
        self.WeatherEncoder = weatherEncoder
        self.WeatherData = {
            "Current": {},
            "Forecast": {},
            "History": []
        }
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
            parts.append(f"{minutes}s")
        parts.append(f"{seconds}s")

        return ' '.join(parts)
        

    def RefreshScreen(self):
        now = datetime.now()
        DayOfWeek = now.strftime("%A")
        FullDate = now.strftime("%B %d, %Y")
        Hour = now.hour
        if (Hour == 0):
            Hour = 12
        if (Hour > 12):
            Hour = Hour - 12
        FullTime = f"{Hour}:" + now.strftime("%M %p")

        FontBig = ("Arial", 40, "bold")
        FontHuge = ("Arial", 90)
        FontTemp = ("Arial", 72, "bold")
        FontEmoji = (self.EmojiFont, 72)
        FontSmallTemp = ("Arial", 46)
        FontSmallEmoji = (self.EmojiFont, 32)
        FontUpdate = ("Arial", 22)

        self.CurrentFrame = ttk.LabelFrame(self.Root, text="Weather Test")
       
        self.canvas.delete("all")
        self.LoadBackgroundImage()
        self.CreateTextWithStroke(DayOfWeek, FontBig, 30, 30)
        self.CreateTextWithStroke(FullDate, FontBig, 30, 90)
        self.CreateTextWithStroke(FullTime, FontHuge, 400, 30)
        lastUpdated = self.WeatherData["Current"]["LastUpdate"].strftime("%Y-%m-%d %I:%M:%S %p")
        uptime = self.GetUptimeString()
        observed = self.WeatherData["Current"]["ObservedTimeLocal"].strftime("%Y-%m-%d %I:%M:%S %p")
        source = self.WeatherData["Current"]["Source"]
        self.canvas.create_text(1900, 1000, text=F"Uptime: {uptime}",fill="#777",anchor="e")
        self.canvas.create_text(1900, 980, text=F"Last Updated: {lastUpdated}",fill="#777",anchor="e")
        self.canvas.create_text(1900, 960, text=F"Observed: {observed}",fill="#777",anchor="e")
        self.canvas.create_text(1900, 940, text=F"Source: {source}",fill="#777",anchor="e")
        if (self.EnableImageTagDisplay):
            self.canvas.create_text(5, 10, text=F"Requested Image Tags: {self.LastBackgroundImageTags}", anchor="w")
            self.canvas.create_text(400, 10, text=F"This Image Tags: {self.ThisImageTags}", anchor="w")
            if (self.ImageTagMessage):
                self.canvas.create_text(800, 10, text=F"Image Message: {self.ImageTagMessage}", anchor="w")


        if (self.WeatherData["Current"]["Source"] == "Station"):
            station = self.WeatherData["Current"]["StationID"]
            self.canvas.create_text(1900, 920, text=F"Station: {station}",fill="#777",anchor="e")
        

        try:
            temp = self.WeatherData["Current"].get("CurrentTempF", "--")
            feelsLikeTemp = self.WeatherData["Current"].get("HeatIndex","--")
            feelsLike = f"Feels Like: {feelsLikeTemp}°"
            state = self.WeatherData["Current"].get("State", "")
            emoji = self.GetWeatherEmoji(state, now.astimezone())
            display = f"{temp}°"
            self.CreateTextWithStroke(display, FontTemp, 1750, 30, anchor="ne")
            self.CreateTextWithStroke(feelsLike, FontBig, 1750, 160, anchor="ne", mainFill="#BBB")
            self.CreateTextWithStroke(emoji["Emoji"], FontEmoji, 1880, 30, anchor="ne", mainFill=emoji["Color"])
            self.CreateTextWithStroke("🌡️", FontSmallEmoji, 1490, 30, anchor="ne", mainFill="red")
            self.CreateTextWithStroke("🌃", FontSmallEmoji, 1500, 90, anchor="ne", mainFill="blue")
            self.CreateTextWithStroke(self.WeatherData["Forecast"]["Daytime"]["HighF"], FontSmallTemp, 1420, 30, anchor="ne", mainFill="red")
            self.CreateTextWithStroke(self.WeatherData["Forecast"]["Nighttime"]["LowF"], FontSmallTemp, 1420, 90, anchor="ne", mainFill="blue")
        except Exception as e:
            self.Log.warn(f"Failed to render weather info: {e}")

        wind_dir = self.WeatherData["Current"].get("WindDirection", 0)
        wind_speed = self.WeatherData["Current"].get("WindSpeedMPH", 0)
        gust_speed = self.WeatherData["Current"].get("GustMPH", 0)
        self.DrawWindIndicator(1700, 350, wind_dir, wind_speed, gust_speed)
        self.DrawRainForecastGraph()
        self.DrawRainSquare()
        self.DrawTemperatureGraph()
        self.DrawHumiditySquare()

        self.Root.after(1000, self.RefreshScreen)

    def DrawTemperatureGraph(self, x=940, y=30, width=360, height=130):
        hourlyTemps = defaultdict(list)
        history = self.WeatherData.get("History", [])

        self.canvas.create_line(x, y, x+width, y, fill="white", width=2, smooth=True)
        self.canvas.create_line(x, y+height, x+width, y+height, fill="white", width=2, smooth=True)
        

        now = datetime.now(timezone.utc)
        
        minTime = now.replace(minute=0,second=0,microsecond=0) - timedelta(hours=24)
        maxTime = now.replace(minute=0,second=0,microsecond=0)
        minTimestamp = now + timedelta(days=5)
        maxTimestamp = now - timedelta(days=5)
        high = self.WeatherData["Forecast"]["Daytime"]["HighF"]
        low = self.WeatherData["Forecast"]["Nighttime"]["LowF"]
        tempRange = max(high - low, 1)
        tempPoints = []
        coords = []

        for timestamp, data in self.WeatherData["History"]:
            utcTimestamp = timestamp
            if "CurrentTempF" in data:
                hourBucket = utcTimestamp.replace(minute=0,second=0,microsecond=0)
                if minTime <= hourBucket <= now:
                    hourlyTemps[hourBucket].append(data["CurrentTempF"])

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

    def DrawHumiditySquare(self, x=1290, y=280, size=100):
        try:
            humidity = self.WeatherData["Current"].get("Humidity", 100)

            fill_ratio = humidity / 100
            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height
            self.CreateTextWithStroke("💦", (self.EmojiFont, 40, "bold"), x + size // 2, y + size // 2, anchor = "center", mainFill="#00F")
            self.canvas.create_rectangle(x, y, x + size, y + size, outline="white", width=2)
            self.canvas.create_rectangle(x + 1, top_fill_y, x + size - 2, y + size - 2, fill="#00BFFF",outline=None)
            label = f"{humidity}%"
            self.CreateTextWithStroke(label, ("Arial", 24, "bold"), x + size // 2, y + size // 2, anchor="center", mainFill="white")
        except Exception as e:
            self.Log.warn(f"Failed to draw humidity square: {e}")

    def DrawRainSquare(self, x=1400, y=280, size=100):
        try:
            rain_inches = self.WeatherData["Current"].get("RainInches", 0)
            max_inches = 2.0

            rain_inches = min(max(rain_inches, 0), max_inches)
            fill_ratio = rain_inches / max_inches

            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height

            self.CreateTextWithStroke("💧", (self.EmojiFont, 40, "bold"), x + size // 2, y + size // 2, anchor="center", mainFill="#00F")
            self.canvas.create_rectangle(x, y, x + size, y + size, outline="white", width=2)
            self.canvas.create_rectangle(x, top_fill_y, x + size, y + size, fill="blue", outline="blue")
            label = f"{rain_inches:.2f}\""
            self.CreateTextWithStroke(label, ("Arial", 24, "bold"), x + size // 2, y + size // 2, anchor="center", mainFill="white")
        except Exception as e:
            self.Log.warn(f"Failed to draw rain square: {e}")

    def DrawRainForecastGraph(self, x_start=30, y_base=850, bar_width=20, bar_spacing=30, bar_max_height=100):
        forecast = self.WeatherData["Forecast"].get("Next24Hours", [])
        if not forecast:
            return

        DailyFont = ("Arial", 14)
        RainAmountFont = ("Arial", 10)
        RainWarningFont = ("Arial", 30)
        WeatherEmojiFront = (self.EmojiFont, 14)
        HasRain = False

        gradientWidth = (bar_width + bar_spacing) * 24
        secondsPerPixel = 86400 / gradientWidth
        colorPixels = self.CalculateMinuteGradients(gradientWidth)
        now = datetime.now()
        gradientHeight = 35
        secondsPastHour = now.minute * 60 + now.second

        firstHour = datetime.strptime(forecast[0]["Time"], "%Y-%m-%d %H:%M")
        currentHour = now.replace(minute=0,second=0,microsecond=0)

        if (firstHour < currentHour):
            secondsPastHour += 60 * 60

        pushRight = int(secondsPastHour / secondsPerPixel) + x_start
        i = 0
        cloudHeight = 8
        for pixel in colorPixels:
            if (pushRight + i > gradientWidth + bar_spacing):
                continue
            fillColor = f"#{pixel["Main"][0]:02x}{pixel["Main"][1]:02x}{pixel["Main"][2]:02x}"
            cloudFillColor = f"#{pixel["Cloud"][0]:02x}{pixel["Cloud"][1]:02x}{pixel["Cloud"][2]:02x}"

           
            self.canvas.create_line(pushRight + i, y_base + bar_max_height, pushRight + i, y_base + bar_max_height + cloudHeight, fill=cloudFillColor)
            self.canvas.create_line(pushRight + i, y_base + bar_max_height + cloudHeight, pushRight + i, y_base + bar_max_height + gradientHeight, fill=fillColor)
            i += 1

        max_rain = 100  # Max rain chance is 100%
        for i, hour_data in enumerate(forecast[:24]):
            rain_chance = hour_data.get("RainChance", 0)
            rain_amount = hour_data.get("PrecipitationInches", 0)
            cloudCoverPercentage = hour_data.get("CloudCoverPercentage", 0)
            if rain_amount > 0:
                HasRain = True
            
            time_str = hour_data.get("Time", "")
            Time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            Hour12 = Time.strftime("%I").lstrip("0")
            AMPM = Time.strftime("%p").lower()[0]
            hour_label = Hour12 + AMPM
            WeatherEmoji = self.GetWeatherEmoji(hour_data.get("ConditionText","--"), Time.astimezone())

            bar_height = (rain_chance / max_rain) * bar_max_height
            x = x_start + i * (bar_width + bar_spacing)

            self.canvas.create_rectangle(
                x, y_base + bar_max_height - bar_height, x + bar_width, y_base + bar_max_height,
                fill="blue", outline=""
            )

            self.CreateTextWithStroke(hour_label, DailyFont, x + 2 + bar_width // 2, y_base - 24, anchor="n")
            if (self.IsRaspberryPi):
                self.canvas.create_text(x + 2 + bar_width // 2, y_base + 107, text=WeatherEmoji["Emoji"], font=WeatherEmojiFront, anchor="n")
            else:
                self.CreateTextWithStroke(WeatherEmoji["Emoji"], WeatherEmojiFront, x + 2 + bar_width // 2, y_base + 107, anchor="n",mainFill=WeatherEmoji["Color"])

            self.CreateTextWithStroke(F"{cloudCoverPercentage}%", RainAmountFont, x + 2 + bar_width // 2, y_base + 135, anchor="n")
            
            if rain_amount > 0:
                self.CreateTextWithStroke(f"{rain_amount}\"", RainAmountFont, x + 2 + bar_width // 2, y_base - 40, anchor="n")

        

        self.canvas.create_line(x_start, y_base, x_start + ((bar_spacing + bar_width) * 24), y_base, fill="white")
        self.canvas.create_line(x_start, y_base + bar_max_height, x_start + ((bar_spacing + bar_width) * 24), y_base + bar_max_height, fill="white")

        if not HasRain:
            self.CreateTextWithStroke("No Rain Detected in the next 24 Hours", RainWarningFont, x_start + ((bar_width + bar_spacing) * 12), y_base + 25, anchor="n", mainFill="#0f0")

    def ToLocalNaive(self, iso_string: str) -> datetime:
        utc = datetime.fromisoformat(iso_string)
        local = utc.astimezone(tz.tzlocal()).replace(tzinfo=None)
        return local

    def CalculateMinuteGradients(self, pixelWidth):
        forecast = self.WeatherData["Forecast"]
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
                {"Name": "Dawn", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunrise"]["AstronomicalTwilight"]) - timedelta(minutes=15), "Color": duskColor},
                {"Name": "Astronomical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunrise"]["AstronomicalTwilight"]), "Color": duskColor},
                {"Name": "Nautical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunrise"]["NauticalTwilight"]), "Color": nauticalTwilightColor},
                {"Name": "Civil Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunrise"]["CivilTwilight"]), "Color": civilTwilightColor},
                {"Name": "Day", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunrise"]["Day"]), "Color": dayColor},
                {"Name": "Sunset", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunset"]["Start"]), "Color": dayColor},
                {"Name": "Civil Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunset"]["CivilTwilight"]), "Color": civilTwilightColor},
                {"Name": "Nautical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunset"]["NauticalTwilight"]), "Color": nauticalTwilightColor},
                {"Name": "Dusk", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunset"]["AstronomicalTwilight"]), "Color": duskColor},
                {"Name": "Night", "Time": self.ToLocalNaive(forecast["SunTimes"]["Today"]["Sunset"]["AstronomicalTwilight"]) + timedelta(minutes=15), "Color": nightColor},
    
                {"Name": "Dawn", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunrise"]["AstronomicalTwilight"]) - timedelta(minutes=15), "Color": duskColor},
                {"Name": "Astronomical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunrise"]["AstronomicalTwilight"]), "Color": duskColor},
                {"Name": "Nautical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunrise"]["NauticalTwilight"]), "Color": nauticalTwilightColor},
                {"Name": "Civil Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunrise"]["CivilTwilight"]), "Color": civilTwilightColor},
                {"Name": "Day", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunrise"]["Day"]), "Color": dayColor},
                {"Name": "Sunset", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunset"]["Start"]), "Color": dayColor},
                {"Name": "Civil Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunset"]["CivilTwilight"]), "Color": civilTwilightColor},
                {"Name": "Nautical Twilight", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunset"]["NauticalTwilight"]), "Color": nauticalTwilightColor},
                {"Name": "Dusk", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunset"]["AstronomicalTwilight"]), "Color": duskColor},
                {"Name": "Night", "Time": self.ToLocalNaive(forecast["SunTimes"]["Tomorrow"]["Sunset"]["AstronomicalTwilight"]) + timedelta(minutes=15), "Color": nightColor},
    
                {"Name": "End", "Time": datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(hours=48), "Color": nightColor}
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
        for h in self.WeatherData["Forecast"]["Next24Hours"]:
            if (h["Time"] == bucketName):
                return h["CloudCoverPercentage"] / 100
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

    def DrawWindIndicator(self, x, y, direction_deg, speed_mph, gust_mph):
        radius = 100

        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="white", width=3)
        font = ("Arial", 22, "bold")
        degreeFont = ("Arial", 18)

        speed_text = f"{speed_mph:.1f} MPH"
        gust_text = f"({gust_mph:.1f} MPH)"

        angle_rad = math.radians(direction_deg - 90)
        end_x = x + math.cos(angle_rad) * radius * 1.2
        end_y = y + math.sin(angle_rad) * radius * 1.2

        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = int((direction_deg + 11.25) % 360 / 22.5)
        compass = directions[index]
        degree_label = f"{direction_deg:.0f}° ({compass})"

        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            self.canvas.create_line(x + dx, y + dy, end_x + dx, end_y + dy, fill="black", width=5, arrow=tk.LAST)

        self.canvas.create_line(x, y, end_x, end_y, fill="white", width=5, arrow=tk.LAST)
        self.CreateTextWithStroke(speed_text, font, x, y - 30, anchor="center")
        self.CreateTextWithStroke(gust_text, font, x, y, anchor="center")
        self.CreateTextWithStroke(degree_label, degreeFont, x, y + 30, anchor="center")


    def GetWeatherEmoji(self, state, time):
        text = state.lower()
        MoonPhase = self.WeatherData["Forecast"].get("MoonPhase", "--").lower()
        IsNight = self.IsNight(time)
        IsSunset = self.IsSunset(time)
        IsSunrise = self.IsSunrise(time)

        if "thunder" in text:
            return {"Emoji": "⛈️", "Color": "#FFD700"}  # Gold
        if "rain" in text or "shower" in text or "drizzle" in text:
            return {"Emoji": "🌧️", "Color": "#1E90FF"}  # Dodger Blue
        if IsNight and "new moon" in MoonPhase:
            return {"Emoji": "🌑", "Color": "#222222"}  # Dark gray
        if IsNight and "full moon" in MoonPhase:
            return {"Emoji": "🌕", "Color": "#FFFFE0"}  # Light Yellow
        if IsNight and "waxing crescent" in MoonPhase:
            return {"Emoji": "🌒", "Color": "#CCCCCC"}
        if IsNight and "first quarter" in MoonPhase:
            return {"Emoji": "🌓", "Color": "#DDDDDD"}
        if IsNight and "waxing gibbous" in MoonPhase:
            return {"Emoji": "🌔", "Color": "#EEEEEE"}
        if IsNight and "waning gibbous" in MoonPhase:
            return {"Emoji": "🌖", "Color": "#EEEEEE"}
        if IsNight and "third quarter" in MoonPhase:
            return {"Emoji": "🌗", "Color": "#DDDDDD"}
        if IsNight and "waning crescent" in MoonPhase:
            return {"Emoji": "🌘", "Color": "#CCCCCC"}
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
        self.Log.info(F"image_dir: {image_dir}")
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
        current_tags = self.GetWeatherTags(now.astimezone())

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
        state = self.WeatherData["Current"].get("State", "").lower()
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
        self.RefreshForecastData();
        self.RefreshCurrentData();
        self.RefreshStationData();
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
        if (not self.EnableTrace):
            return

        hourlyTemps = defaultdict(list)
        for timestamp, data in self.WeatherData["History"]:
            utcTimestamp = timestamp.astimezone(timezone.utc)
            if "CurrentTempF" in data:
                hourBucket = utcTimestamp.replace(minute=0, second=0, microsecond=0)
                hourlyTemps[hourBucket].append(data["CurrentTempF"])
        
        hourBuckets = hourlyTemps.keys()
        self.Log.debug(F"{reason}: hourBuckets = {hourBuckets} ({len(hourBuckets)})")

    def GrabHistoricalData(self):
        historicalData = self.WeatherService.GetStationHistory();
        self.WeatherData["History"] = historicalData;
        self.DebugBuckets("GrabHistoricalData");

    def AppendToHistory(self):
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=26)
        currentData = self.WeatherData["Current"];

        self.DebugBuckets("RefreshStationdata Pre-Append")
        self.WeatherData["History"].append((now, currentData))
        self.DebugBuckets("RefreshStationdata Post-Append")
        newHistory = []
        for (timestamp, content) in self.WeatherData["History"]:
            if (timestamp >= cutoff):
                newHistory.append((timestamp,content))

        self.WeatherData["History"] = newHistory
        self.DebugBuckets("RefreshStationdata Post-Filter")

    def RefreshStationData(self):
        currentData = self.WeatherService.OverlayStationData(self.WeatherData["Current"])

        self.WeatherData["Current"] = currentData
        self.AppendToHistory()

        if (self.EnableTrace):
            self.Log.debug(F"RefreshStationData: {self.WeatherData['Current']}")
        self.Root.after(60 * 1000, self.RefreshStationData)
        
    def RefreshCurrentData(self):
        currentData = self.WeatherService.GetCurrentData()
        self.WeatherData["Current"] = currentData
        self.AppendToHistory()

        if (self.EnableTrace):
            self.Log.debug(F"RefreshCurrentData: {currentData}")
        self.ChangeBackgroundImage()

        self.Root.after(60 * 15 * 1000, self.RefreshCurrentData)

    def ClassifyWeatherBackground(self):
        condition = self.WeatherData["Current"].get("State", "").lower()
        is_night = self.IsNight(datetime.now().astimezone())

        now = datetime.now().astimezone()

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
            sunriseToday = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunrise"]["AstronomicalTwilight"]).astimezone(time.tzinfo)
            sunsetToday = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunset"]["AstronomicalTwilight"]).astimezone(time.tzinfo)

            sunriseTomorrow = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Tomorrow"]["Sunrise"]["AstronomicalTwilight"]).astimezone(time.tzinfo)
            sunsetTomorrow = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Tomorrow"]["Sunset"]["AstronomicalTwilight"]).astimezone(time.tzinfo)


            return time < sunriseToday or sunsetToday < time < sunriseTomorrow or sunsetTomorrow < time
        except Exception as e:
            self.Log.warn(f"is_night exception: {e}")
            return False

    def IsSunset(self, time):
        try:
            start = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunset"]["Start"]).astimezone(time.tzinfo)
            end = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunset"]["AstronomicalTwilight"]).astimezone(time.tzinfo)

            tomorrowstart = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunset"]["Start"]).astimezone(time.tzinfo)
            tomorrowend = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunset"]["AstronomicalTwilight"]).astimezone(time.tzinfo)

            if (self.EnableTrace):
                self.Log.debug(F"Sunset: {start} < {time} < {end} = {start < time < end} or {tomorrowstart} <= {time} <= {tomorrowend} = {tomorrowstart <= time <= tomorrowend}")

            return start <= time <= end or tomorrowstart <= time <= tomorrowend

        except Exception as e:
            self.Log.warn(f"Failed to determine sunset time: {e}")
            return False

    def IsSunrise(self, time):
        try:
            start = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunrise"]["AstronomicalTwilight"]).astimezone(time.tzinfo)
            end = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Today"]["Sunrise"]["Day"]).astimezone(time.tzinfo)

            tomorrowstart = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Tomorrow"]["Sunrise"]["AstronomicalTwilight"]).astimezone(time.tzinfo)
            tomorrowend = datetime.fromisoformat(self.WeatherData["Forecast"]["SunTimes"]["Tomorrow"]["Sunrise"]["Day"]).astimezone(time.tzinfo)
            return start <= time <= end or tomorrowstart <= time <= tomorrowend
        except:
            return False


    def RefreshForecastData(self):
        self.WeatherData["Forecast"] = self.WeatherService.GetForecastData()
        if (self.EnableTrace):
            self.Log.debug(F"RefreshForecastData: {self.WeatherData['Forecast']}")
            self.Log.debug("----")

        self.Root.after(60 * 60 * 1000, self.RefreshForecastData)
            
    def CreateTextWithStroke(self, text, font, x, y, anchor = "nw", mainFill="white"):
        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            self.canvas.create_text(x + dx, y + dy, text=text, font=font, fill="black", anchor=anchor)

        self.canvas.create_text(x, y, text=text, font=font, fill=mainFill, anchor=anchor)
