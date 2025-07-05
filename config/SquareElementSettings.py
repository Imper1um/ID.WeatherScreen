from dataclasses import dataclass

from .ElementSettings import ElementSettings

@dataclass 
class SquareElementSettings(ElementSettings):
    Size: int = 0
    OutlineColor: str = None
    OutlineWidth: int = None
    FillColor: str = None