from dataclasses import dataclass,field

from .TextElementSettings import TextElementSettings
from .SizeElementSettings import SizeElementSettings

@dataclass
class TemperatureGraphSettings(SizeElementSettings):
    SmallText: TextElementSettings = field(default_factory=lambda:TextElementSettings(Enabled=False,FontFamily="Arial", FontSize=7, FillColor="white", Anchor="n", Stroke=False))
    TimeTemps: TextElementSettings = field(default_factory=lambda:TextElementSettings(Enabled=False,FontFamily="Arial", FontSize=7, FillColor="white", Anchor="n", Stroke=False))