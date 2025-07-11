from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from config.IconType import IconType
from data.WeatherConditions import WeatherConditions


@dataclass
class CurrentData:
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
    ObservedTimeUtc: Optional[datetime] = None
    ObservedTimeLocal: Optional[datetime] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    LastBackgroundImageTags: Optional[str] = None
    LastBackgroundImagePath: Optional[str] = None
    LastBackgroundImageChange: Optional[datetime] = None
    CurrentBackgroundImagePath: Optional[str] = None
    ThisImageTags: Optional[str] = None
    ImageTagMessage: Optional[str] = None
    
    Conditions: Optional[WeatherConditions] = None
    