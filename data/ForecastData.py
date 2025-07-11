from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from config.IconType import IconType
from data.MoonPhase import MoonPhase
from data.WeatherConditions import WeatherConditions

@dataclass
class DaytimeData:
    RainChance: Optional[float] = None
    SnowChance: Optional[float] = None
    Rain: Optional[float] = None
    Snow: Optional[float] = None
    High: Optional[float] = None
    ForecastText: Optional[str] = None


@dataclass
class NighttimeData:
    Low: Optional[float] = None
    ForecastText: Optional[str] = None


@dataclass
class HourlyForecast:
    Time: Optional[str] = None
    Temperature: Optional[float] = None
    WindDirection: Optional[int] = None
    ConditionText: Optional[str] = None
    UVIndex: Optional[float] = None
    HeatIndex: Optional[float] = None
    FeelsLike: Optional[float] = None
    DewPoint: Optional[float] = None
    Pressure: Optional[float] = None
    Humidity: Optional[float] = None
    RainChance: Optional[float] = None
    SnowChance: Optional[float] = None

    Conditions: Optional[WeatherConditions] = field(default_factory=lambda: WeatherConditions())


@dataclass
class RainTimesData:
    Start: Optional[datetime] = None
    End: Optional[datetime] = None
    AlreadyRaining: Optional[bool] = None

@dataclass
class ForecastData:
    Moon: Optional[MoonPhase] = None
    Daytime: DaytimeData = field(default_factory=DaytimeData)
    Nighttime: NighttimeData = field(default_factory=NighttimeData)
    Next24Hours: List[HourlyForecast] = field(default_factory=list)
    RainTimes: RainTimesData = field(default_factory=RainTimesData)