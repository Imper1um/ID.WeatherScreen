import json, logging, os, random
import exiftool

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dateutil import tz
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk

from config.SettingsEnums import *
from config.WeatherConfig import WeatherConfig

from core.drawing.RainForecastGraph import RainForecastGraph
from core.drawing.CanvasWrapper import CanvasWrapper
from core.drawing.HumiditySquare import HumiditySquare
from core.drawing.RainSquare import RainSquare
from core.drawing.TemperatureGraph import TemperatureGraph
from core.drawing.WindIndicator import WindIndicator
from helpers import DateTimeHelpers, PlatformHelpers
from helpers.WeatherHelpers import WeatherHelpers
from services.WeatherService import WeatherService

from data.CurrentData import CurrentData
from data.ForecastData import ForecastData, MoonPhase 
from data.HistoryData import HistoryData, HistoryLine
from data.SunData import SunData

class WeatherDisplay:
    def __init__(self, root, weatherService: WeatherService, weatherConfig: WeatherConfig):
        self.Config = weatherConfig
        self.Log = logging.getLogger("WeatherDisplay")
        self.BasePath = weatherConfig._basePath
        self.Log.debug(F"BasePath: {self.BasePath}")
        self.EmojiFont = "Segoe UI Emoji"
        self.Root = root
        if (PlatformHelpers.IsRaspberryPi()):
            self.EmojiFont = "Noto Color Emoji"
            self.Root.overrideredirect(True)
            self.Root.attributes('-fullscreen', True)
            self.Root.attributes('-type', "splash")
        else:
            self.Root.geometry("1920x1080")
        self.FirstTry = True
        self.WeatherService = weatherService
        self.CurrentData: Optional[CurrentData] = None
        self.ForecastData: Optional[ForecastData] = None
        self.HistoryData: Optional[HistoryData] = None
        self.SunData: Optional[SunData] = None
        self.LastBackgroundImageType = None
        self.LastBackgroundImageTags = None
        self.LastBackgroundImageChange = None


        self.Root.title("Weather Display")
        self.current_labels = {}
        self.forecast_labels = {}

        canvas = tk.Canvas(self.Root, width=1920, height=1080, bg="#0f0", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.CanvasWrapper = CanvasWrapper(canvas, "tk")

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
                    self.Log.warning(F'No image matches tags ["{s}","{c}"]')

    def Render(self, wrapper: CanvasWrapper):
        now = datetime.now()

        wrapper.Clear()
        wrapper.BackgroundImage(self.LastBackgroundImagePath)
        DayOfWeek = now.strftime("%A")
        wrapper.TextElement(DayOfWeek, self.Config.Weather.DayOfWeek)
        wrapper.FormattedTextElement(now, self.Config.Weather.FullDate)
        wrapper.FormattedTextElement(now, self.Config.Weather.Time)
        uptime = F"Uptime: {DateTimeHelpers.GetReadableTimeBetween(self.Begin)}"
        wrapper.TextElement(uptime, self.Config.Weather.Uptime)
        wrapper.FormattedTextElement(self.CurrentData.LastUpdate, self.Config.Weather.LastUpdated)
        wrapper.FormattedTextElement(self.CurrentData.ObservedTimeLocal, self.Config.Weather.Observed)
        source = F"Source: {self.CurrentData.Source}"
        wrapper.TextElement(source, self.Config.Weather.Source)

        imageTags = F"Requested Image Tags: {self.LastBackgroundImageTags} // This Image Tags: {self.ThisImageTags}"
        if (self.ImageTagMessage):
            imageTags += F" // Image Message: {self.ImageTagMessage}"

        wrapper.TextElement(imageTags, self.Config.Weather.ImageTags)

        if (self.CurrentData.Source == "Station"):
            station = F"Station: {self.CurrentData.StationId}"
            wrapper.TextElement(station, self.Config.Weather.Station)

        try:
            temp = self.CurrentData.CurrentTemp
            feelsLikeTemp = self.CurrentData.FeelsLike
            feelsLike = f"Feels Like: {feelsLikeTemp}°"
            state = self.CurrentData.State
            emoji = WeatherHelpers.GetWeatherEmoji(state, now, self.ForecastData, self.SunData)
            display = f"{temp}°"
            wrapper.TextElement(display, self.Config.Weather.CurrentTemp)
            wrapper.TextElement(feelsLike, self.Config.Weather.FeelsLike)
            wrapper.EmojiElement(emoji["Emoji"], self.Config.Weather.CurrentTempEmoji)
            wrapper.TextElement(self.ForecastData.Daytime.High, self.Config.Weather.TempHigh)
            wrapper.TextElement(self.ForecastData.Nighttime.Low, self.Config.Weather.TempLow)
        except Exception as e:
            self.Log.warning(f"Failed to render weather info: {e}")

        TemperatureGraph.Draw(wrapper, self.HistoryData, self.ForecastData, self.Config.Weather.TemperatureGraph)
        HumiditySquare.Draw(wrapper, self.CurrentData, self.Config.Weather.HumiditySquare)
        RainSquare.Draw(wrapper, self.CurrentData, self.Config.Weather)
        WindIndicator.Draw(wrapper, self.Config.Weather, self.CurrentData, self.HistoryData)
        RainForecastGraph.Draw(wrapper, self.ForecastData, self.SunData, self.Config.Weather)

    def RefreshScreen(self):
        self.CurrentFrame = ttk.LabelFrame(self.Root, text="Weather Test")

        self.Render(self.CanvasWrapper)
       
        self.Root.after(1000, self.RefreshScreen)

    def ToLocalNaive(self, iso_string: str) -> datetime:
        utc = datetime.fromisoformat(iso_string)
        local = utc.astimezone(tz.tzlocal()).replace(tzinfo=None)
        return local

    def GetAllBackgroundImages(self):
        image_dir = os.path.join(self.BasePath, "assets", "backgrounds")
        self.Log.debug(F"image_dir: {image_dir}")
        if not os.path.exists(image_dir):
            self.Log.warning(f"Background directory does not exist: {image_dir}")
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

        if WeatherHelpers.IsSunrise(self.SunData, time):
            tags.append("Sunrise")
        elif WeatherHelpers.IsSunset(self.SunData, time):
            tags.append("Sunset")
        elif WeatherHelpers.IsNight(self.SunData, time):
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

        for key, tag in condition_map.items():
            if key in state:
                tags.append(tag)
                break
        else:
            tags.append("Unknown")

        return tags


    def StartDataRefresh(self):
        self.GrabHistoricalData();
        self.RefreshCurrentData();
        self.RefreshSunData();
        self.RefreshForecastData();
        self.ChangeBackgroundImage()
        self.RefreshScreen();

        if (PlatformHelpers.IsRaspberryPi()):
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
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=26)
        currentData = self.CurrentData;

        self.DebugBuckets("RefreshStationdata Pre-Append")
        self.HistoryData.Lines.append(currentData)
        self.DebugBuckets("RefreshStationdata Post-Append")
        newHistory = []
        for line in self.HistoryData.Lines:
            timestamp = line.ObservedTimeUtc
            if (DateTimeHelpers.GreaterThanOrEqual(timestamp, cutoff)):
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

    


    def RefreshForecastData(self):
        self.ForecastData = self.WeatherService.GetForecastData()
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"RefreshForecastData: {self.ForecastData}")
            self.Log.debug("----")

        self.Root.after(60 * 60 * 1000, self.RefreshForecastData)
            
