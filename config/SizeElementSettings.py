from dataclasses import dataclass

from config.ElementSettings import ElementSettings

@dataclass
class SizeElementSettings(ElementSettings):
    Width: int = 0
    Height: int = 0