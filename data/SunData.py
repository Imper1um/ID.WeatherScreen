from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class SunTimeSet:
    AstronomicalTwilight: Optional[datetime] = None
    NauticalTwilight: Optional[datetime] = None
    CivilTwilight: Optional[datetime] = None
    Day: Optional[datetime] = None


@dataclass
class SunsetSet:
    Start: Optional[datetime] = None
    CivilTwilight: Optional[datetime] = None
    NauticalTwilight: Optional[datetime] = None
    AstronomicalTwilight: Optional[datetime] = None

@dataclass
class DailySunTimes:
    Sunrise: SunTimeSet = field(default_factory=SunTimeSet)
    Sunset: SunsetSet = field(default_factory=SunsetSet)

@dataclass
class SunData:
    Today: DailySunTimes = field(default_factory=DailySunTimes)
    Tomorrow: DailySunTimes = field(default_factory=DailySunTimes)