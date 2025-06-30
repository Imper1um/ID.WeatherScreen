from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, Optional, List

class MoonPhase(Enum):
    NewMoon = "New Moon"
    WaxingCrescent = "Waxing Crescent"
    FirstQuarter = "First Quarter"
    WaxingGibbous = "Waxing Gibbous"
    FullMoon = "Full Moon"
    WaningGibbous = "Waning Gibbous"
    LastQuarter = "Last Quarter"
    WaningCrescent = "Waning Crescent"

    @classmethod
    def FromString(cls, phase_str: str):
        for phase in cls:
            if phase.value.lower() == phase_str.lower():
                return phase
        if (phase_str.lower() == "third quarter"):
            return MoonPhase.LastQuarter
        raise ValueError(f"Unknown moon phase: {phase_str}")

    @property
    def ToEmoji(self) -> str:
        return {
            MoonPhase.NewMoon: "🌑",
            MoonPhase.WaxingCrescent: "🌒",
            MoonPhase.FirstQuarter: "🌓",
            MoonPhase.WaxingGibbous: "🌔",
            MoonPhase.FullMoon: "🌕",
            MoonPhase.WaningGibbous: "🌖",
            MoonPhase.LastQuarter: "🌗",
            MoonPhase.WaningCrescent: "🌘",
        }.get(self, "❓")

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
    CloudCoverPercentage: Optional[float] = None
    WindDirection: Optional[int] = None
    WindSpeed: Optional[float] = None
    WindGust: Optional[float] = None
    ConditionText: Optional[str] = None
    UVIndex: Optional[float] = None
    HeatIndex: Optional[float] = None
    FeelsLike: Optional[float] = None
    DewPoint: Optional[float] = None
    Pressure: Optional[float] = None
    Humidity: Optional[float] = None
    PrecipitationRain: Optional[float] = None
    RainChance: Optional[float] = None
    PrecipitationSnow: Optional[float] = None
    SnowChance: Optional[float] = None

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