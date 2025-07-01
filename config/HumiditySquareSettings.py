from dataclasses import dataclass, field

from config.SquareElementSettings import SquareElementSettings
from config.TextElementSettings import TextElementSettings

@dataclass
class HumiditySquareSettings(SquareElementSettings):
    Emoji: TextElementSettings = field(default_factory=lambda: TextElementSettings(Anchor="center",FontSize=40, FontWeight="bold",FillColor="#00F"))
    Text: TextElementSettings = field(default_factory=lambda: TextElementSettings(Anchor="center",FontSize=24,FontWeight="bold",FillColor="white"))
