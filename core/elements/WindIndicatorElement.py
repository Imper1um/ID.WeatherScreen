import logging
import math

from config.SettingsEnums import WindType
from config.WeatherSettings import WeatherSettings
from .ElementBase import ElementBase
from .ElementRefresh import ElementRefresh
from core.store import WeatherDisplayStore
from core.drawing import CanvasWrapper
from helpers.Delay import Delay
from data import *
import tkinter as tk

class WindIndicatorElement(ElementBase):
    def __init__(self, wrapper: CanvasWrapper, settings: WeatherSettings):
        self.Wrapper = wrapper
        self.Settings = settings

        er = ElementRefresh(ElementRefresh.OnUpdateCurrentData, ElementRefresh.OnTimer)
        er.Delay = Delay.FromMinutes(2)
        self.ElementRefresh = er

    def Initialize(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.WindIndicator
        if not config.Enabled:
            return self.ElementRefresh

        x = config.X
        y = config.Y
        radius = config.Size

        self.Wrapper.Oval(x - radius, y - radius, x + radius, y + radius, outlineColor="white", borderWidth=3)

        store.WindIndicator.HistoryArrows = []
        for i in range(config.HistoryArrows):
            fade = 0.1 + (0.5 * (i + 1) / config.HistoryArrows)
            gray_value = int(255 * fade)
            gray = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            fadedX = x
            fadedY = y - radius * 0.95
            arrow = self.Wrapper.Line(x, y, fadedX, fadedY, fillColor=gray, width=3, arrow=tk.LAST)
            store.WindIndicator.HistoryArrows.append(arrow)

        end_x = x
        end_y = y - radius * 1.2
        store.WindIndicator.PrimaryArrow = self.Wrapper.Line(x, y, end_x, end_y, fillColor="white", width=5, arrow=tk.LAST, stroke=True)

        addon = "MPH" if self.Settings.Wind == WindType.MPH else "KPH"
        store.WindIndicator.Wind = self.Wrapper.TextElement(f"-- {addon}", config.Wind, xOffset=x, yOffset=y - 30)
        store.WindIndicator.Gust = self.Wrapper.TextElement(f"(-- {addon})", config.Gust, xOffset=x, yOffset=y)
        store.WindIndicator.Direction = self.Wrapper.TextElement(f"--° (--)", config.Direction, xOffset=x, yOffset=y + 30)

        return self.Refresh(store, forecast, current, history, sunData)

    def Refresh(self, store: WeatherDisplayStore, forecast: ForecastData, current: CurrentData, history: HistoryData, sunData: SunData) -> ElementRefresh:
        config = self.Settings.WindIndicator
        if not config.Enabled:
            return self.ElementRefresh

        x = config.X
        y = config.Y
        radius = config.Size

        wind = current.WindSpeed or 0
        gust = current.WindGust or 0
        direction = current.WindDirection or 0
        addon = "MPH" if self.Settings.Wind == WindType.MPH else "KPH"

        angle_rad = math.radians(direction - 90)
        end_x = x + math.cos(angle_rad) * radius * 1.2
        end_y = y + math.sin(angle_rad) * radius * 1.2

        self.Wrapper.MoveDouble(store.WindIndicator.PrimaryArrow, x, y, end_x, end_y)

        self.Wrapper.UpdateText(store.WindIndicator.Wind, f"{wind:.1f} {addon}")
        self.Wrapper.UpdateText(store.WindIndicator.Gust, f"({gust:.1f} {addon})")

        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = int((direction + 11.25) % 360 / 22.5)
        compass = directions[index]
        self.Wrapper.UpdateText(store.WindIndicator.Direction, f"{direction:.0f}° ({compass})")

        deduped_lines = []
        last_direction = direction
        for line in history.Lines[1:]:
            if not hasattr(line, "WindDirection") or line.WindDirection is None:
                continue
            if line.WindDirection != last_direction:
                deduped_lines.append(line)
                last_direction = line.WindDirection
            if len(deduped_lines) >= config.HistoryArrows:
                break

        historyDirections = []

        for i, (line, arrowStore) in enumerate(zip(deduped_lines, store.WindIndicator.HistoryArrows)):
            pastDirection = line.WindDirection
            angleRad = math.radians(pastDirection - 90)
            fadedX = x + math.cos(angleRad) * radius * 0.95
            fadedY = y + math.sin(angleRad) * radius * 0.95
            self.Wrapper.MoveDouble(arrowStore, x, y, fadedX, fadedY)
            historyDirections.append(pastDirection)

        logging.debug(F'{historyDirections}')
        return self.ElementRefresh
