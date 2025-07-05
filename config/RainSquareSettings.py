from dataclasses import dataclass

from .HumiditySquareSettings import HumiditySquareSettings

@dataclass
class RainSquareSettings(HumiditySquareSettings):
    MaxRain: float = 2.0
