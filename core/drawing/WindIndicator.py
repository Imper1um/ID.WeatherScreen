import math

import tkinter as tk

from config.SettingsEnums import WindType
from config.WeatherSettings import WeatherSettings
from data.CurrentData import CurrentData
from data.HistoryData import HistoryData
from .CanvasWrapper import CanvasWrapper

class WindIndicator:
    def Draw(wrapper:CanvasWrapper, settings:WeatherSettings, current:CurrentData, history:HistoryData):
        if (not settings.WindIndicator.Enabled):
            return

        config = settings.WindIndicator
        radius = config.Size
        x = config.X
        y = config.Y

        wind = current.WindSpeed
        gust = current.WindGust
        direction = current.WindDirection
        addon = "MPH" if settings.Wind == WindType.MPH else "KPH"

        wrapper.Oval(x - radius, y - radius, x + radius, y + radius, outlineColor="white", borderWidth=3)
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
            line for line in reversed(history.Lines[:-1])
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
            wrapper.Line(x, y, fadedX, fadedY, fillColor=gray, width=3, arrow=tk.LAST)

        wrapper.Line(x, y, end_x, end_y, fillColor="white", width=5, arrow=tk.LAST, stroke=True)
        wrapper.TextElement(speed_text, config.Wind, xOffset=x, yOffset= y - 30)
        wrapper.TextElement(gust_text, config.Gust, xOffset=x, yOffset=y)
        wrapper.TextElement(degree_label, config.Direction, xOffset=x, yOffset=y + 30)