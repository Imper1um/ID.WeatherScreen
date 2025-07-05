from dataclasses import dataclass, field

from .SquareElementSettings import SquareElementSettings
from .TextElementSettings import TextElementSettings

@dataclass
class WindIndicatorSettings(SquareElementSettings):
    HistoryArrows: int = 5
    Wind: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial", FontSize=22, FontWeight="bold", FillColor="white", Anchor="center"))
    Gust: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial", FontSize=22, FontWeight="bold", FillColor="white", Anchor="center"))
    Direction: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontFamily="Arial", FontSize=18, FillColor="white", Anchor="center"))
