from dataclasses import dataclass, field
from typing import List

@dataclass
class SelectionSettings:
    History: str = "WeatherUnderground"
    Forecast: str = "WeatherAPI"
    Station: str = "WeatherUnderground"
    Sun: str = "SunriseSunset"
    Current: List[str] = field(default_factory=lambda: ["WeatherAPI", "WeatherUnderground"])
