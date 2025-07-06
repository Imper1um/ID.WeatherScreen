from dataclasses import fields
import importlib
import inspect
import pkgutil
import json, logging, os, random
import exiftool

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from dateutil import tz

import tkinter as tk
from tkinter import Tk

from core.elements.ElementRefresh import ElementRefresh

from .WeatherScheduler import WeatherScheduler

from config.SettingsEnums import *
from config.WeatherConfig import WeatherConfig
from config.WeatherSettings import WeatherSettings

from core.drawing.CanvasWrapper import CanvasWrapper
from core.elements.ElementBase import ElementBase
from core.store import WeatherDisplayStore
from helpers import DateTimeHelpers, PlatformHelpers
from helpers.WeatherHelpers import WeatherHelpers
from services.WeatherService import WeatherService

from data.CurrentData import CurrentData
from data.ForecastData import ForecastData
from data.HistoryData import HistoryData
from data.SunData import SunData

def GetAllElements(wrapper: CanvasWrapper, settings: WeatherSettings) -> List[ElementBase]:
    foundItems: List[ElementBase] = []
    import core.elements
    package = core.elements
    baseClass = ElementBase

    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_name = f"{package.__name__}.{module_name}"
        try:
            module = importlib.import_module(full_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, baseClass) and obj is not baseClass and obj.__module__ == full_name:
                    try:
                        instance = obj(wrapper, settings)
                        foundItems.append(instance)
                        logging.debug(f"Element Found: {full_name}.{name}")
                    except Exception as e:
                        logging.warning(f"Failed to instantiate {name}: {e}")
        except Exception as e:
            logging.debug(f"Skipping module {full_name}: {e}")

    return foundItems

class WeatherDisplay:
    def __init__(self, root:Tk, weatherService: WeatherService, weatherConfig: WeatherConfig):
        self.Config = weatherConfig
        self.Log = logging.getLogger("WeatherDisplay")
        self.BasePath = weatherConfig._basePath
        self.Log.debug(F"BasePath: {self.BasePath}")
        self.Root = root
        if (PlatformHelpers.IsRaspberryPi()):
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

        self.Root.title("Weather Display")
        self.current_labels = {}
        self.forecast_labels = {}

        canvas = tk.Canvas(self.Root, width=1920, height=1080, bg="#0f0", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.CanvasWrapper = CanvasWrapper(canvas, "tk")

        self.Begin = datetime.now()

        self.CheckBackgroundImages()

        self.WeatherDisplayStore = WeatherDisplayStore()
        self.Elements = GetAllElements(self.CanvasWrapper, self.Config.Weather)

        self.WeatherScheduler = WeatherScheduler(self)

    def CheckBackgroundImages(self):
        allBackgroundImages = self.GetAllBackgroundImages()
        self.Log.debug(F"{len(allBackgroundImages)} images found.")
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

    def Initialize(self, wrapper: CanvasWrapper, store: WeatherDisplayStore, elements:list[ElementBase], history:HistoryData, current:CurrentData, forecast:ForecastData, sun:SunData):
        wrapper.Clear()
        store.Background = wrapper.BackgroundImage(self.CurrentData.LastBackgroundImagePath)

        timers:List[Tuple[ElementBase, ElementRefresh]] = []

        for e in elements:
            er = e.Initialize(store, forecast, current, history, sun)
            timers.append((e, er))

        self.WeatherScheduler.UpdateTimers(timers)

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

        if (self.CurrentData.CurrentBackgroundImagePath != self.CurrentData.LastBackgroundImagePath and self.WeatherDisplayStore.Background is not None and self.CanvasWrapper.Canvas.winfo_ismapped()):
            self.WeatherDisplayStore.Background.ChangeImage(self.CurrentData.LastBackgroundImagePath)
            self.CurrentData.CurrentBackgroundImagePath = self.CurrentData.LastBackgroundImagePath


        ShouldChange = False
        if (self.CurrentData.LastBackgroundImageTags is None or set(current_tags) != set(self.CurrentData.LastBackgroundImageTags)):
            ShouldChange = True
        if self.CurrentData.LastBackgroundImageChange is None or now - self.CurrentData.LastBackgroundImageChange >= timedelta(minutes=10):
            ShouldChange = True

        if not ShouldChange and self.CurrentData.LastBackgroundImagePath == self.CurrentData.CurrentBackgroundImagePath:
            self.Root.after(60 * 1000, self.ChangeBackgroundImage)
            return
        elif not ShouldChange:
            self.Root.after(1000, self.ChangeBackgroundImage)
            return

        self.CurrentData.LastBackgroundImageChange = now
        self.CurrentData.LastBackgroundImageTags = current_tags
        
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

        self.CurrentData.ThisImageTags = SelectedFile["Tags"]
        self.CurrentData.LastBackgroundImagePath = SelectedFile["Path"]


        if (self.WeatherDisplayStore.Background is not None and self.CanvasWrapper.Canvas.winfo_ismapped()):
            self.WeatherDisplayStore.Background.ChangeImage(self.CurrentData.LastBackgroundImagePath)
            self.CurrentData.CurrentBackgroundImagePath = self.CurrentData.LastBackgroundImagePath
            self.WeatherScheduler.UpdateBackground(self.WeatherDisplayStore, self.ForecastData, self.CurrentData, self.HistoryData, self.SunData)
            self.Root.after(60 * 1000, self.ChangeBackgroundImage)
        else:
            self.Root.after(1000, self.ChangeBackgroundImage)
        
        

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
        allElements = GetAllElements(self.CanvasWrapper, self.Config.Weather)

        self.GrabHistoricalData();
        self.RefreshCurrentData();
        self.RefreshSunData();
        self.RefreshForecastData();
        self.ChangeBackgroundImage()

        self.Initialize(self.CanvasWrapper, self.WeatherDisplayStore, allElements, self.HistoryData, self.CurrentData, self.ForecastData, self.SunData)

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

    def GrabHistoricalData(self):
        historicalData = self.WeatherService.GetHistoryData();
        self.HistoryData = historicalData

    def RefreshSunData(self):
        now = datetime.now()
        self.SunData = self.WeatherService.GetSunData(self.CurrentData.Latitude, self.CurrentData.Longitude, now);

        tomorrow = (now + timedelta(days = 1)).replace(hour = 0, minute = 0, second = 5, microsecond = 0)
        delay = (tomorrow - now).total_seconds() * 1000
        self.WeatherScheduler.UpdateSunData(self.WeatherDisplayStore, self.ForecastData, self.CurrentData, self.HistoryData, self.SunData)
        self.Root.after(int(delay), self.RefreshSunData)

    def AppendToHistory(self):
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=26)
        currentData = self.CurrentData;

        self.HistoryData.Lines.append(currentData)
        newHistory = []
        for line in self.HistoryData.Lines:
            timestamp = line.ObservedTimeUtc
            if (DateTimeHelpers.GreaterThanOrEqual(timestamp, cutoff)):
                newHistory.append(line)

        self.HistoryData.Lines = newHistory
        self.WeatherScheduler.UpdateHistoryData(self.WeatherDisplayStore, self.ForecastData, self.CurrentData, self.HistoryData, self.SunData)

    def RefreshCurrentData(self):
        currentData = self.WeatherService.GetCurrentData()
        if (self.CurrentData is None):
            self.CurrentData = currentData;
        else:
            for f in fields(currentData):
                value = getattr(currentData, f.name)
                if value is not None:
                    setattr(self.CurrentData, f.name, value)
            
        self.AppendToHistory()

        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"RefreshCurrentData: {currentData}")

        self.WeatherScheduler.UpdateCurrentData(self.WeatherDisplayStore, self.ForecastData, self.CurrentData, self.HistoryData, self.SunData)
        self.Root.after(60 * 1000, self.RefreshCurrentData)

    def RefreshForecastData(self):
        self.ForecastData = self.WeatherService.GetForecastData()
        if (self.Config.Logging.EnableTrace):
            self.Log.debug(F"RefreshForecastData: {self.ForecastData}")
            self.Log.debug("----")

        self.WeatherScheduler.UpdateForecastData(self.WeatherDisplayStore, self.ForecastData, self.CurrentData, self.HistoryData, self.SunData)
        self.Root.after(60 * 60 * 1000, self.RefreshForecastData)
            
