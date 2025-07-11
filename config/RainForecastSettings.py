from dataclasses import dataclass, field

from config.FormattedTextElementSettings import FormattedTextElementSettings
from config.StackedEmojiElementSettings import StackedEmojiElementSettings
from config.StackedIconElementSettings import StackedIconElementSettings
from .ElementSettings import ElementSettings
from .TextElementSettings import TextElementSettings
from .SkyGradientSettings import SkyGradientSettings

@dataclass
class RainForecastSettings(ElementSettings):
    BarWidth: int = 20
    BarSpacing: int = 20
    BarMaxHeight: int = 100
    RainAmount: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial",FontSize=10, Anchor="n"))
    Hour: FormattedTextElementSettings = field(default_factory=lambda:FormattedTextElementSettings(FontFamily="Arial",FontSize=14, Anchor="n", Format="%-I%-p"))
    Emoji: StackedEmojiElementSettings = field(default_factory=lambda:StackedEmojiElementSettings(Enabled=False,FontSize=14, Anchor="n", Stroke=False))
    Icon: StackedIconElementSettings = field(default_factory=lambda:StackedIconElementSettings(FontSize=14, Anchor="n", Stroke=False, Width=35, Height=35))
    CloudCover: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial",FontSize=10, Anchor="n"))
    SkyGradient: SkyGradientSettings = field(default_factory=lambda:SkyGradientSettings())
    NoRainWarning: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=30, FontFamily="Arial", Anchor="n", FillColor="#0f0"))
