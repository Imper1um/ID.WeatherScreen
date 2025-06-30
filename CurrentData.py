from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class CurrentData:
    Source: Optional[str] = None
    StationId: Optional[str] = None
    WindDirection: Optional[int] = None
    WindSpeed: Optional[float] = None
    WindGust: Optional[float] = None
    Humidity: Optional[float] = None
    CurrentTemp: Optional[float] = None
    FeelsLike: Optional[float] = None
    HeatIndex: Optional[float] = None
    DewPoint: Optional[float] = None
    UVIndex: Optional[float] = None
    State: Optional[str] = None
    Pressure: Optional[float] = None
    Rain: Optional[float] = None
    Snow: Optional[float] = None
    CloudCover: Optional[int] = None
    Visibility: Optional[float] = None
    LastUpdate: Optional[datetime] = None
    ObservedTimeUtc: Optional[datetime] = None
    ObservedTimeLocal: Optional[datetime] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None