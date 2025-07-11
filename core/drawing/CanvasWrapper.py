from datetime import datetime

from PIL import Image, ImageTk
from config import FormattedTextElementSettings, TextElementSettings
from config.SquareElementSettings import SquareElementSettings
from config.StackedEmojiElementSettings import StackedEmojiElementSettings
from config.StackedIconElementSettings import StackedIconElementSettings
from core.drawing.CachedImage import CachedImage
from core.store.EmojiStore import EmojiStore
from data.EmojiDisplay import EmojiDisplay
from data.IconDisplay import IconDisplay
from .ElementStore import ElementStore
from helpers import DateTimeHelpers
from helpers import PlatformHelpers

class CanvasWrapper:
    def __init__(self, canvas, canvasType:str):
        self.Canvas = canvas
        self.CanvasType = canvasType
        self.EmojiFont = "Noto Color Emoji" if PlatformHelpers.IsRaspberryPi() else "Segoe UI Emoji"

        self.CachedBackgroundImages: dict[str, ImageTk.PhotoImage] = {}
        self.CachedImages: list[CachedImage] = []
        self.CurrentElements: list[ElementStore] = []

    def FormattedTextElement(self, date: datetime, settings: FormattedTextElementSettings, xOffset: int = 0, yOffset: int = 0) -> ElementStore:
        if (not settings.Enabled):
            return

        return self.TextElement(DateTimeHelpers.HourSafeToString(date, settings.Format), settings, xOffset, yOffset)

    def EmojiElement(self, text:str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0) -> ElementStore:
        if (not settings.Enabled):
            return None

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

        return self.Text(text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, anchor, fillColor, stroke, strokeWidth, strokeColor, justify)

    def TextElement(self, text:str, settings: TextElementSettings, xOffset: int = 0, yOffset: int = 0) -> ElementStore:
        if (not settings.Enabled):
            return None

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
        stroke = True
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

        return self.Text(text, settings.X + xOffset, settings.Y + yOffset, fontFamily, fontSize, fontWeight, anchor, fillColor, stroke, strokeWidth, strokeColor, justify)

    def EmojiText(self, text: str, x: int, y: int, fontSize: int = 16, fontWeight: str = "normal", anchor:str = "nw", fillColor:str = "white", stroke:bool = False, strokeAmount: int = 2, strokeColor: str = "black", justify: str = "left") -> ElementStore:
        return self.Text(text, x, y, self.EmojiFont, fontSize, fontWeight, anchor, fillColor, stroke, strokeAmount, strokeColor, justify)

    def Text(self, text: str, x: int, y: int, fontFamily: str = "Arial", fontSize: int = 16, fontWeight: str = "normal", anchor:str = "nw", fillColor:str = "white", stroke:bool = False, strokeAmount: int = 2, strokeColor: str = "black", justify: str = "left") -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            fontDescriptor = [fontFamily, fontSize, fontWeight]
            if (stroke and strokeColor and strokeAmount):
                xStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                yStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                for xs in xStroke:
                    for ys in yStroke:
                        es.AddBackingElement(self.Canvas.create_text(x + xs, y + ys, text = text, anchor = anchor, fill = strokeColor, font = fontDescriptor, justify = justify));
            
            es.AddPrimaryElement(self.Canvas.create_text(x, y, text = text, anchor = anchor, fill = fillColor, font = fontDescriptor, justify = justify));

        self.CurrentElements.append(es)
        return es

    def Line(self, x1, y1, x2, y2, width:int = 2, arrow:str = None, fillColor: str = "white", smooth: bool = False, stroke: bool = False, strokeColor: str = "black", strokeAmount: int = 2) -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            if (stroke and strokeColor and strokeAmount):
                xStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                yStroke = list(range(-1 * strokeAmount, strokeAmount + 1))
                for xs in xStroke:
                    for ys in yStroke:
                        es.AddBackingElement(self.Canvas.create_line(x1 + xs, y1 + ys, x2 + xs, y2 + ys, fill = strokeColor, width = width, smooth = smooth, arrow = arrow))
                        

            es.AddPrimaryElement(self.Canvas.create_line(x1, y1, x2, y2, fill = fillColor, width = width, smooth = smooth, arrow= arrow))

        self.CurrentElements.append(es)
        return es

    def SquareElement(self, settings: SquareElementSettings, xOffset: int = 0, yOffset: int = 0) -> ElementStore:
        if (not settings.Enabled):
            return None

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

        return self.Rectangle(x1 + xOffset, y1 + yOffset, x2 + xOffset, y2 + yOffset, borderWidth=borderWidth, fillColor=fillColor, outlineColor=borderColor)

    def Rectangle(self, x1:int, y1:int, x2:int, y2:int, borderWidth: int = 2, fillColor: str = '', outlineColor: str = "white") -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            es.AddPrimaryElement(self.Canvas.create_rectangle(x1, y1, x2, y2, outline=outlineColor, fill=fillColor, width=borderWidth))

        self.CurrentElements.append(es)
        return es

    def Oval(self, x1: int, y1:int, x2:int, y2: int, borderWidth: int = 2, fillColor: str = '', outlineColor: str = "white") -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            es.AddPrimaryElement(self.Canvas.create_oval(x1, y1, x2, y2, width=borderWidth, fill=fillColor, outline=outlineColor))

        self.CurrentElements.append(es)
        return es

    def BackgroundImage(self, path: str) -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            if path in self.CachedBackgroundImages:
                es.AddPrimaryElement(self.Canvas.create_image(0, 0, image=self.CachedBackgroundImages[path], anchor="nw"))
                self.CurrentElements.append(es)
                return es
            imgtk = None
            if self.Canvas.winfo_ismapped():
                img = Image.open(path)
                img = img.resize((self.Canvas.winfo_width(), self.Canvas.winfo_height()), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self.CachedBackgroundImages[path] = imgtk

            es.AddPrimaryElement(self.Canvas.create_image(0, 0, image=imgtk, anchor="nw"))

        self.CurrentElements.append(es)
        return es

    def Image(self, path: str, x: int, y:int, width:int, height:int) -> ElementStore:
        es = ElementStore(self)
        if (self.CanvasType == "tk"):
            cachedImage = next(
                    (img for img in self.CachedImages
                        if img.Path == path
                        and img.Width == width
                        and img.Height == height), None
                )

            if cachedImage:
                es.AddPrimaryElement(self.Canvas.create_image(x, y, image=cachedImage.Image, anchor="nw"))

            imgtk = None
            img = Image.open(path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)
            self.CachedImages.append(CachedImage(path, imgtk, width, height))

            es.AddPrimaryElement(self.Canvas.create_image(x, y, image=imgtk, anchor="nw"))

        self.CurrentElements.append(es)
        return es

    def ChangeBackgroundImage(self, es:ElementStore, path:str):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            if path in self.CachedBackgroundImages:
                self.Canvas.itemconfig(es.PrimaryElement, image=self.CachedBackgroundImages[path])
            elif self.Canvas.winfo_ismapped():
                img = Image.open(path)
                img = img.resize((self.Canvas.winfo_width(), self.Canvas.winfo_height()), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self.CachedBackgroundImages[path] = imgtk
                self.Canvas.itemconfig(es.PrimaryElement, image=imgtk)

    def ChangeImage(self, es:ElementStore, path:str, width: int, height: int):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            cachedImage = next(
                    (img for img in self.CachedImages
                        if img.Path == path
                        and img.Width == width
                        and img.Height == height), None
                )

            if cachedImage:
                self.Canvas.itemconfig(es.PrimaryElement, image=cachedImage.Image)

            else:
                img = Image.open(path)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                self.CachedImages.append(CachedImage(path, imgtk, width, height))
                self.Canvas.itemconfig(es.PrimaryElement, image=imgtk)
    
    def UpdateText(self, es:ElementStore, text: str):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            for s in es.BackingElements:
                self.Canvas.itemconfig(s, text=text)
            self.Canvas.itemconfig(es.PrimaryElement, text=text)

    def MoveSingle(self, es:ElementStore, x:int, y:int):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            for s in es.BackingElements:
                self.Canvas.coords(s, x, y)
            self.Canvas.coords(es.PrimaryElement, x, y)

    def MoveDouble(self, es:ElementStore, x1:int, y1:int, x2:int, y2:int):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            for s in es.BackingElements:
                self.Canvas.coords(s, x1, y1, x2, y2)
            self.Canvas.coords(es.PrimaryElement, x1, y1, x2, y2)

    def Delete(self, es:ElementStore):
        if (es.IsDeleted):
            return

        if (self.CanvasType == "tk"):
            for e in es.BackingElements:
                self.Canvas.delete(e)
            self.Canvas.delete(es.PrimaryElement)

        es.IsDeleted = True

        if (es in self.CurrentElements):
            self.CurrentElements.remove(es)

    def Clear(self):
        if (self.CanvasType == "tk"):
            self.Canvas.delete("all")
            for e in self.CurrentElements:
                e.IsDeleted = True

    def StackedEmojiElement(self, emoji:EmojiDisplay, settings: StackedEmojiElementSettings, xOffset: int = 0, yOffset: int = 0) -> EmojiStore:
        if (not settings.Enabled):
            return None

        fontFamily = self.EmojiFont
        if (settings.FontFamily):
            fontFamily = settings.FontFamily
        fontSize = 12
        if (settings.FontSize):
            fontSize = settings.FontSize
        fontWeight = "normal"
        if (settings.FontWeight):
            fontWeight = settings.FontWeight
        anchor = "center"
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

        def CreateAdjustedEmoji(el:TextElementSettings, layerText:str, fontSizeOffset:int):
            adjFontFamily = el.FontFamily if el.FontFamily is not None else fontFamily
            adjFontSize = fontSize + fontSizeOffset + el.FontSize
            adjFontWeight = el.FontWeight if el.FontWeight is not None else fontWeight
            adjAnchor = el.Anchor if el.Anchor is not None else anchor
            adjStroke = el.Stroke if el.Stroke is not None else stroke
            adjStrokeColor = el.StrokeColor if el.StrokeColor is not None else strokeColor
            adjStrokeWidth = el.StrokeWidth if el.StrokeWidth is not None else strokeWidth
            adjFillColor = el.FillColor if el.FillColor is not None else fillColor
            adjJustify = el.Justify if el.Justify is not None else justify
            adjX = settings.X + xOffset + el.X
            adjY = settings.Y + yOffset + el.Y

            return self.Text(layerText, adjX, adjY, adjFontFamily, adjFontSize, adjFontWeight, adjAnchor, adjFillColor, adjStroke, adjStrokeWidth, adjStrokeColor, adjJustify)

        return EmojiStore(
            back=CreateAdjustedEmoji(settings.Back, emoji.Back, 0),
            middle=CreateAdjustedEmoji(settings.Middle, emoji.Middle, -2),
            front=CreateAdjustedEmoji(settings.Front, emoji.Front, -4)
            )

    def StackedIconElement(self, path:str, icon:IconDisplay, settings: StackedIconElementSettings, xOffset: int = 0, yOffset: int = 0) -> EmojiStore:
        if (not settings.Enabled):
            return None

        fontFamily = self.EmojiFont
        if (settings.FontFamily):
            fontFamily = settings.FontFamily
        fontSize = 12
        if (settings.FontSize):
            fontSize = settings.FontSize
        fontWeight = "normal"
        if (settings.FontWeight):
            fontWeight = settings.FontWeight
        anchor = "center"
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

        xPos = settings.X + xOffset
        yPos = settings.Y + yOffset
        textPosX = xPos
        textPosY = yPos
        width = settings.Width
        height = settings.Height
        if (anchor == "n" or anchor == "center" or anchor == "s"):
            textPosX += int(settings.Width / 2)
        if (anchor == "w" or anchor == "center" or anchor == "e"):
            textPosY += int(settings.Height / 2)
        if (anchor == "ne" or anchor == "e" or anchor == "se"):
            textPosX += settings.Width
        if (anchor == "sw" or anchor == "s" or anchor == "sw"):
            textPosY += settings.Height

        iconImg = self.Image(path, xPos, yPos, width, height)

        def CreateAdjustedEmoji(el:TextElementSettings, layerText:str, fontSizeOffset:int):
            adjFontFamily = el.FontFamily if el.FontFamily is not None else fontFamily
            adjFontSize = fontSize + fontSizeOffset + el.FontSize
            adjFontWeight = el.FontWeight if el.FontWeight is not None else fontWeight
            adjAnchor = el.Anchor if el.Anchor is not None else anchor
            adjStroke = el.Stroke if el.Stroke is not None else stroke
            adjStrokeColor = el.StrokeColor if el.StrokeColor is not None else strokeColor
            adjStrokeWidth = el.StrokeWidth if el.StrokeWidth is not None else strokeWidth
            adjFillColor = el.FillColor if el.FillColor is not None else fillColor
            adjJustify = el.Justify if el.Justify is not None else justify
            adjX = textPosX + el.X
            adjY = textPosY + el.Y

            return self.Text(layerText, adjX, adjY, adjFontFamily, adjFontSize, adjFontWeight, adjAnchor, adjFillColor, adjStroke, adjStrokeWidth, adjStrokeColor, adjJustify)

        return EmojiStore(
            back=iconImg,
            middle=CreateAdjustedEmoji(settings.Middle, icon.Middle, -2),
            front=CreateAdjustedEmoji(settings.Front, icon.Front, -4)
            )

