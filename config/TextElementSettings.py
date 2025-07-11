from dataclasses import dataclass
from typing import Optional

from .ElementSettings import ElementSettings

@dataclass
class TextElementSettings(ElementSettings):
    FillColor: Optional[str] = None
    FontFamily: Optional[str] = None
    FontWeight: Optional[str] = None
    FontSize: Optional[int] = None
    Anchor: Optional[str] = None
    Stroke: Optional[bool] = None
    StrokeColor: Optional[str] = None
    StrokeWidth: Optional[int] = None
    Justify: Optional[str] = None