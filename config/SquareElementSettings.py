from dataclasses import dataclass

from config.ElementSettings import ElementSettings

@dataclass 
class SquareElementSettings(ElementSettings):
    Size: int = 0