from datetime import datetime

from PIL import Image, ImageTk
from config import FormattedTextElementSettings, TextElementSettings
from config.SquareElementSettings import SquareElementSettings
from helpers import DateTimeHelpers
from helpers import PlatformHelpers


class CanvasWrapper:
    def __init__(self, canvas, canvasType:str):
        self.Canvas = canvas
        self.CanvasType = canvasType
        self.EmojiFont = "Noto Color Emoji" if PlatformHelpers.IsRaspberryPi() else "Segoe UI Emoji"

        self.CachedImages: dict[str, ImageTk.PhotoImage] = {}

    def FormattedTextElement(self, date: datetime, settings: FormattedTextElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        self.TextElement(DateTimeHelpers.HourSafeToString(date, settings.Format), settings, xOffset, yOffset)

    def EmojiElement(self, text:str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        fontFamily = self.EmojiFont
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
        stroke = False
        strokeColor = "#000"
        strokeWidth = 2
        if (settings.Stroke is not None):
            stroke = settings.Stroke
        if (settings.StrokeColor):
            strokeColor = settings.StrokeColor
        if (settings.StrokeWidth):
            strokeWidth = settings.StrokeWidth
        fillColor = "#FFF"
        if (settings.FillColor):
            fillColor = settings.FillColor
        justify = "left"
        if (settings.Justify):
            justify = settings.Justify

        self.Text(text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, anchor, fillColor, stroke, strokeWidth, strokeColor, justify)

    def TextElement(self, text:str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0):
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
        stroke = False
        strokeColor = "#000"
        strokeWidth = 2
        if (settings.Stroke is not None):
            stroke = settings.Stroke
        if (settings.StrokeColor):
            strokeColor = settings.StrokeColor
        if (settings.StrokeWidth):
            strokeWidth = settings.StrokeWidth
        fillColor = "#FFF"
        if (settings.FillColor):
            fillColor = settings.FillColor
        justify = "left"
        if (settings.Justify):
            justify = settings.Justify

        self.Text(text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, anchor, fillColor, stroke, strokeWidth, strokeColor, justify)


    def Text(self, text: str, x: int, y: int, fontFamily: str = "Arial", fontSize: int = 16, fontWeight: str = "normal", anchor:str = "nw", fillColor:str = "white", stroke:bool = False, strokeAmount: int = 2, strokeColor: str = "black", justify: str = "left"):
        if (self.CanvasType == "tk"):
            fontDescriptor = [fontFamily, fontSize, fontWeight]
            if (stroke and strokeColor and strokeAmount):
                xStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                yStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                for xs in xStroke:
                    for ys in yStroke:
                        self.Canvas.create_text(x + xs, y + ys, text = text, anchor = anchor, fill = strokeColor, font = fontDescriptor, justify = justify);
            
            self.Canvas.create_text(x, y, text = text, anchor = anchor, fill = fillColor, font = fontDescriptor, justify = justify);

    def EmojiText(self, text: str, x: int, y: int, fontSize: int = 16, fontWeight: str = "normal", anchor:str = "nw", fillColor:str = "white", stroke:bool = False, strokeAmount: int = 2, strokeColor: str = "black", justify: str = "left"):
        self.Text(text, x, y, self.EmojiFont, fontSize, fontWeight, anchor, fillColor, stroke, strokeAmount, strokeColor, justify)

    def Line(self, x1, y1, x2, y2, width:int = 2, arrow:str = None, fillColor: str = "white", smooth: bool = False, stroke: bool = False, strokeColor: str = "black", strokeAmount: int = 2):
        if (self.CanvasType == "tk"):
            if (stroke and strokeColor and strokeAmount):
                xStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                yStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                for xs in xStroke:
                    for ys in yStroke:
                        self.Canvas.create_line(x1 + xs, y1 + ys, x2 + xs, y2 + ys, fill = strokeColor, width = width, smooth = smooth, arrow = arrow)

            self.Canvas.create_line(x1, y1, x2, y2, fill = fillColor, width = width, smooth = smooth, arrow= arrow)

    def SquareElement(self, settings: SquareElementSettings, xOffset: int = 0, yOffset: int = 0):
        if (not settings.Enabled):
            return

        x1 = settings.X
        x2 = settings.X + settings.Size
        y1 = settings.Y
        y2 = settings.Y + settings.Size
        borderWidth = 2
        if (settings.OutlineWidth):
            borderWidth = settings.OutlineWidth
        borderColor = "white"
        if (settings.OutlineColor):
            borderColor = settings.OutlineColor
        fillColor = None
        if (settings.FillColor):
            fillColor = settings.FillColor

        self.Rectangle(x1 + xOffset, y1 + yOffset, x2 + xOffset, y2 + yOffset, borderWidth=borderWidth, fillColor=fillColor, outlineColor=borderColor)

    def Rectangle(self, x1:int, y1:int, x2:int, y2:int, borderWidth: int = 2, fillColor: str = '', outlineColor: str = "white"):
        if (self.CanvasType == "tk"):
            self.Canvas.create_rectangle(x1, y1, x2, y2, outline=outlineColor, fill=fillColor, width=borderWidth)

    def Oval(self, x1: int, y1:int, x2:int, y2: int, borderWidth: int = 2, fillColor: str = '', outlineColor: str = "white"):
        if (self.CanvasType == "tk"):
            self.Canvas.create_oval(x1, y1, x2, y2, width=borderWidth, fill=fillColor, outline=outlineColor)

    def BackgroundImage(self, path: str):
        if (self.CanvasType == "tk"):
            if path in self.CachedImages:
                self.Canvas.create_image(0, 0, image=self.CachedImages[path], anchor="nw")

            img = Image.open(path)
            img = img.resize((self.Canvas.winfo_width(), self.Canvas.winfo_height()), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)
            self.CachedImages[path] = imgtk
            self.Canvas.create_image(0, 0, image=imgtk, anchor="nw")

    def Clear(self):
        if (self.CanvasType == "tk"):
            self.Canvas.delete("all")


