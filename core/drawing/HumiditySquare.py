import logging
from config.HumiditySquareSettings import HumiditySquareSettings
from core.drawing.CanvasWrapper import CanvasWrapper
from data.CurrentData import CurrentData


class HumiditySquare:
    def Draw(wrapper:CanvasWrapper, current:CurrentData, config:HumiditySquareSettings):
        if (not current or not current.Humidity or not config.Enabled):
            return

        try:
            humidity = current.Humidity
            x = config.X
            y = config.Y
            size = config.Size

            fill_ratio = humidity / 100
            fill_height = int(size * fill_ratio)
            top_fill_y = y + size - fill_height
            wrapper.Rectangle(x + 1, top_fill_y, x + size - 2, y + size - 2, fillColor="#00BFFF",outlineColor=None)
            wrapper.Rectangle(x, y, x + size, y + size, outlineColor="white", borderWidth=2)
            wrapper.EmojiElement("💦", config.Emoji, xOffset =  x + size // 2, yOffset = y + size // 2)
            label = f"{humidity}%"
            wrapper.TextElement(label, config.Text, xOffset = x + size // 2, yOffset = y + size // 2)
        except Exception as e:
            logging.warning(f"Failed to draw humidity square: {e}")