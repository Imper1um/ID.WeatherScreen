import logging
from config.RainSquareSettings import RainSquareSettings
from config.SettingsEnums import PrecipitationType
from config.WeatherSettings import WeatherSettings
from .CanvasWrapper import CanvasWrapper
from data.CurrentData import CurrentData

class RainSquare:
    def Draw(wrapper:CanvasWrapper, current:CurrentData, settings:WeatherSettings):
        if (not current or not current.Rain or not settings.RainSquare.Enabled):
            return

        config = settings.RainSquare

        try:
            max_inches = config.MaxRain
            size = config.Size
            x = config.X
            y = config.Y

            rain_inches = current.Rain
            max_inches = config.MaxRain
            rain_inches = min(max(rain_inches, 0), max_inches)
            fill_ratio = rain_inches / max_inches

            rainAddon = '"' if settings.Precipitation == PrecipitationType.IN else 'MM'

            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height

            wrapper.Rectangle(x, top_fill_y, x + size, y + size, fillColor="blue", outlineColor="blue")
            wrapper.Rectangle(x, y, x + size, y + size, outlineColor="white", borderWidth=2)
            wrapper.EmojiElement("💧", config.Emoji, xOffset=x + size // 2, yOffset= y + size // 2)
            label = f"{rain_inches:.2f}{rainAddon}"
            wrapper.TextElement(label, config.Text, xOffset=x + size // 2, yOffset=y + size // 2)
        except Exception as e:
            logging.warning(f"Failed to draw rain square: {e}")