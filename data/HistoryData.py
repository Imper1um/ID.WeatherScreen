from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class HistoryLine:
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
    Pressure: Optional[float] = None
    Rain: Optional[float] = None
    Snow: Optional[float] = None
    CloudCover: Optional[int] = None
    Visibility: Optional[float] = None
    LastUpdate: Optional[datetime] = None
    ObservedTimeLocal: Optional[datetime] = None
    ObservedTimeUtc: Optional[datetime] = None

@dataclass
class HistoryData:
    Lines: List[HistoryLine] = field(default_factory=list)