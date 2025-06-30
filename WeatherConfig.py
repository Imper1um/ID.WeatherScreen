import json
from dataclasses import dataclass, asdict, field
import dataclasses
from pathlib import Path
import logging
import collections.abc
from enum import Enum
from typing import List, Optional, get_origin, get_args, Union

import dataclasses
from enum import Enum
from typing import get_origin, get_args

def from_dict(cls, data: dict):
    if not dataclasses.is_dataclass(cls):
        return data  # not a dataclass; just return raw value

    init_kwargs = {}

    for field in dataclasses.fields(cls):
        if not field.init:
            continue

        field_value = data.get(field.name, dataclasses.MISSING)
        if field_value is dataclasses.MISSING:
            continue

        field_type = field.type
        origin = get_origin(field_type)

        if origin is Union and type(None) in get_args(field_type):
            field_type = [t for t in get_args(field_type) if t != type(None)][0]

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            init_kwargs[field.name] = field_type(field_value)

        elif dataclasses.is_dataclass(field_type):
            init_kwargs[field.name] = from_dict(field_type, field_value)

        elif origin is list and get_args(field_type):
            item_type = get_args(field_type)[0]
            if dataclasses.is_dataclass(item_type):
                init_kwargs[field.name] = [from_dict(item_type, i) for i in field_value]
            elif isinstance(item_type, type) and issubclass(item_type, Enum):
                init_kwargs[field.name] = [item_type(i) for i in field_value]
            else:
                init_kwargs[field.name] = field_value

        else:
            init_kwargs[field.name] = field_value

    return cls(**init_kwargs)


@dataclass
class ChatGPTSettings:
    Key: str = ""
    Model: str = "gpt-4o"

@dataclass
class LoggingSettings:
    EnableTrace: bool = False
    EnableDebug: bool = False
    LoggingLevel: str = "INFO"

@dataclass
class ServiceSettings:
    Key: str = ""

@dataclass
class SelectionSettings:
    History: str = "WeatherUnderground"
    Forecast: str = "WeatherAPI"
    Station: str = "WeatherUnderground"
    Sun: str = "SunriseSunset"
    Current: List[str] = field(default_factory=lambda: ["WeatherAPI", "WeatherUnderground"])

@dataclass
class ServicesSettings:
    WeatherAPI: ServiceSettings = field(default_factory=ServiceSettings)
    WeatherUnderground: ServiceSettings = field(default_factory=ServiceSettings)
    Selections: SelectionSettings = field(default_factory=SelectionSettings)

@dataclass
class ElementSettings:
    Enabled: bool = True
    X: int = 0
    Y: int = 0

@dataclass
class TextElementSettings(ElementSettings):
    FillColor: Optional[str] = None
    FontFamily: Optional[str] = None
    FontWeight: Optional[str] = None
    FontSize: Optional[int] = None
    Anchor: Optional[str] = None
    Stroke: bool = True

@dataclass
class FormattedTextElementSettings(TextElementSettings):
    Format: Optional[str] = None

@dataclass
class SizeElementSettings(ElementSettings):
    Width: int = 0
    Height: int = 0

class TemperatureType(Enum):
    F = "F"
    C = "C"

    @property
    def description(self):
        return {
            TemperatureType.F: "Fahrenheit (°F)",
            TemperatureType.C: "Celsius (°C)"
        }[self]

class PressureType(Enum):
    MB = "MB"
    HG = "HG"

    @property
    def description(self):
        return {
            PressureType.MB: "Millibars (mb)",
            PressureType.HG: "Inches of Mercury (inHg)"
        }[self]

class WindType(Enum):
    MPH = "MPH"
    KPH = "KPH"

    @property
    def description(self):
        return {
            WindType.MPH: "Miles per Hour (mph)",
            WindType.KPH: "Kilometers per Hour (kph)"
        }[self]

class VisibilityType(Enum):
    Miles = "Miles"
    Kilometers = "Kilometers"

    @property
    def description(self):
        return {
            VisibilityType.Miles: "Miles",
            VisibilityType.Kilometers: "Kilometers"
        }[self]

class PrecipitationType(Enum):
    MM = "MM"
    IN = "IN"

    @property
    def description(self):
        return {
            PrecipitationType.MM: "Millimeters (mm)",
            PrecipitationType.IN: "Inches (in)"
        }[self]

@dataclass
class WeatherSettings:
    Location: str = ""
    StationCode: str = ""
    Temperature: TemperatureType = TemperatureType.F
    Pressure: PressureType = PressureType.MB
    Wind: WindType = WindType.MPH
    Visibility: VisibilityType = VisibilityType.Miles
    Precipitation: PrecipitationType = PrecipitationType.IN
    ImageTags: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=5,Y=10,Enabled=False, Stroke=False))
    Uptime: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900,Y=1000,FillColor="#777",Anchor="e", Stroke=False))
    LastUpdated: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900,Y=980,FillColor="#777",Anchor="e", Stroke=False))
    Observed: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900,Y=960,FillColor="#777",Anchor="e", Stroke=False))
    Source: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900,Y=940,FillColor="#777",Anchor="e", Stroke=False))
    DayOfWeek: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=30,Y=30,FillColor="#FFF",FontSize=40,FontWeight="bold"))
    FullDate: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=30,Y=90,FillColor="#FFF",FontSize=40,FontWeight="bold",Format="%B %d, %Y"))
    Time: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=400, Y=30,FillColor="#FFF",FontSize=90,FontWeight="bold",Format="%-I:%M %p"))
    Station: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900, Y=920, FillColor="#777", Anchor="e", Stroke=False))
    CurrentTempEmoji: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1880, Y=30, Anchor="ne", FontSize=72, Stroke=False))
    CurrentTemp: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1750, Y=30, Anchor="ne", FontSize=72, FontWeight="bold"))
    FeelsLike: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1750, Y=160, Anchor="ne", FillColor="#BBB", FontWeight="bold", FontSize=40))
    TempHigh: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1420,Y=30,Anchor="ne", FillColor="red", FontWeight="bold", FontSize=46))
    TempLow: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1420,Y=90,Anchor="ne", FillColor="blue", FontWeight="bold", FontSize=46))

def enum_safe_asdict(obj):
    if isinstance(obj, Enum):
        return obj.value
    elif dataclasses.is_dataclass(obj):
        result = {}
        for f in dataclasses.fields(obj):
            if f.metadata.get("serialize", True):
                value = getattr(obj, f.name)
                result[f.name] = enum_safe_asdict(value)
        return result
    elif isinstance(obj, dict):
        return {k: enum_safe_asdict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [enum_safe_asdict(v) for v in obj]
    else:
        return obj

@dataclass
class WeatherConfig:
    Logging: LoggingSettings = field(default_factory=LoggingSettings)
    Services: ServicesSettings = field(default_factory=ServicesSettings)
    ChatGPT: ChatGPTSettings = field(default_factory=ChatGPTSettings)
    Weather: WeatherSettings = field(default_factory=WeatherSettings)

    _configFileName: str = field(default="weatherscreen.config", init=False, repr=False, compare=False, metadata={"serialize":False})
    _basePath: Path = field(default=Path(__file__).resolve().parent, init=False, repr=False, compare=False, metadata={"serialize":False})

    @classmethod
    def load(cls) -> "WeatherConfig":
        config_path = cls._basePath / cls._configFileName
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return from_dict(cls, data)
            except Exception as e:
                logging.warning(f"Could not read config file: {e}")
                return cls()
        else:
            config = cls()
            config.save()
            return config

    

    def save(self):
        config_path = self._basePath / self._configFileName
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(enum_safe_asdict(self), f, indent=4)
        except Exception as e:
            logging.error(f"Could not save config file: {e}")

