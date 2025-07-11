from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from data.WeatherConditions import WeatherConditions


@dataclass
class HistoryLine:
    Source: Optional[str] = None
    StationId: Optional[str] = None
    WindDirection: Optional[int] = None
    Humidity: Optional[float] = None
    CurrentTemp: Optional[float] = None
    FeelsLike: Optional[float] = None
    HeatIndex: Optional[float] = None
    DewPoint: Optional[float] = None
    UVIndex: Optional[float] = None
    Pressure: Optional[float] = None
    LastUpdate: Optional[datetime] = None
    ObservedTimeLocal: Optional[datetime] = None
    ObservedTimeUtc: Optional[datetime] = None

    Conditions: Optional[WeatherConditions] = field(default_factory=lambda: WeatherConditions())

@dataclass
class HistoryData:
    Lines: List[HistoryLine] = field(default_factory=list)