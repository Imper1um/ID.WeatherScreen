from dataclasses import dataclass, field

from .SelectionSettings import SelectionSettings
from .ServiceSettings import ServiceSettings

@dataclass
class ServicesSettings:
    WeatherAPI: ServiceSettings = field(default_factory=ServiceSettings)
    WeatherUnderground: ServiceSettings = field(default_factory=ServiceSettings)
    Selections: SelectionSettings = field(default_factory=SelectionSettings)
