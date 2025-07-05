from dataclasses import dataclass, field
from .ElementSettings import ElementSettings
from .TextElementSettings import TextElementSettings
from .SkyGradientSettings import SkyGradientSettings

@dataclass
class RainForecastSettings(ElementSettings):
    BarWidth: int = 20
    BarSpacing: int = 20
    BarMaxHeight: int = 100
    RainAmount: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial",FontSize=10, Anchor="n"))
    Hour: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial",FontSize=14, Anchor="n"))
    Emoji: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=14, Anchor="n"))
    CloudCover: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial",FontSize=10, Anchor="n"))
    SkyGradient: SkyGradientSettings = field(default_factory=lambda:SkyGradientSettings())
    NoRainWarning: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=30, FontFamily="Arial", Anchor="n", FillColor="#0f0"))
