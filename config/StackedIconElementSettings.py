from dataclasses import dataclass, field
from typing import Optional

from config.TextElementSettings import TextElementSettings

@dataclass
class StackedIconElementSettings(TextElementSettings):
    Front: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=0, Anchor="center", Stroke=False))
    Middle: TextElementSettings = field(default_factory=lambda:TextElementSettings(FontSize=0, Anchor="center", Stroke=False))
    Height: int = 100
    Width: int = 100