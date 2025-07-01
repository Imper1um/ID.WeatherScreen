from dataclasses import dataclass

from .ElementSettings import ElementSettings

@dataclass 
class SquareElementSettings(ElementSettings):
    Size: int = 0