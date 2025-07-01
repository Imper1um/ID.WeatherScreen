from dataclasses import dataclass

from config.HumiditySquareSettings import HumiditySquareSettings

@dataclass
class RainSquareSettings(HumiditySquareSettings):
    MaxRain: float = 2.0
