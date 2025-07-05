from dataclasses import dataclass

from .ElementSettings import ElementSettings

@dataclass
class SizeElementSettings(ElementSettings):
    Width: int = 0
    Height: int = 0