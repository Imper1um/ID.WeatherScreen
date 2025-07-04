import datetime, logging
from PIL import ImageFont

from .FontFinder import FontFinder
from .Platform import Platform

from config.FormattedTextElementSettings import FormattedTextElementSettings
from config.TextElementSettings import TextElementSettings


class DrawRender:
    EmojiFont: str = "Noto Color Emoji" if Platform.IsRaspberryPi() else "Segoe UI Emoji"
    Log = logging.getLogger("DrawRender")
    

    def ImageText(destination, text, x, y, fontFamily, fontSize, fontWeight, fillColor, anchor:str="nw", stroke:bool = False):
        try:
            font = FontFinder.GetFont(fontFamily, fontSize)
        except Exception as e:
            DrawRender.Log.warning(f"Could not load truetype font '{fontFamily}': {e}")
            font = ImageFont.load_default()

        try:
            text_bbox = font.getbbox(str(text))
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except Exception as e:
            DrawRender.Log.warning(f"Failed to calculate text bbox: {e}")
            text_width, text_height = 0, 0

        if anchor == "center":
            x -= text_width // 2
            y -= text_height // 2
        elif anchor == "e":
            x += text_width
        elif anchor == "s":
            y += text_height

        if stroke:
            strokeColor = "black"
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    destination.text((x + dx, y + dy), str(text), font=font, fill=strokeColor)
        destination.text((x, y), str(text), font=font, fill=fillColor)

    def FormattedText(destination, drawType, date: datetime, settings: FormattedTextElementSettings):
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

        DrawRender.Text(destination, drawType, date.strftime(f), settings)
    
    def Text(destination, drawType: str, text: str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0, type=type):
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
            if (drawType == "tk"):
                DrawRender.CreateTextWithStroke(destination, text, font, settings.X + xOffset, settings.Y + yOffset, **s)
            elif (drawType == "image"):
                DrawRender.ImageText(destination, text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, settings.FillColor, anchor, True)
        else:
            s = {
                "fill": settings.FillColor,
                "font": font,
                "anchor": anchor
            }
            s = {k: v for k, v in s.items() if v is not None}
            if (drawType == "tk"):
                destination.create_text(settings.X + xOffset, settings.Y + yOffset, text=text, **s)
            elif (drawType == "image"):
                DrawRender.ImageText(destination, text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, settings.FillColor, anchor)

    def EmojiText(destination, drawType, text: str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        fontFamily = DrawRender.EmojiFont
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
        if (drawType == "tk"):
            destination.create_text(settings.X + xOffset, settings.Y + yOffset, text=text, **s)
        elif (drawType == "image"):
            DrawRender.ImageText(destination, text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, "#000", anchor)

    def CreateTextWithStroke(destination, text, font, x, y, anchor = "nw", mainFill="white"):
        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            destination.create_text(x + dx, y + dy, text=text, font=font, fill="black", anchor=anchor)

        destination.create_text(x, y, text=text, font=font, fill=mainFill, anchor=anchor)
