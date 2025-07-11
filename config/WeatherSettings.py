from dataclasses import dataclass, field

from .SettingsEnums import *
from .TextElementSettings import TextElementSettings
from .FormattedTextElementSettings import FormattedTextElementSettings
from .WindIndicatorSettings import WindIndicatorSettings
from .HumiditySquareSettings import HumiditySquareSettings
from .RainSquareSettings import RainSquareSettings
from .RainForecastSettings import RainForecastSettings
from .SizeElementSettings import SizeElementSettings
from .TemperatureGraphSettings import TemperatureGraphSettings
from .StackedEmojiElementSettings import StackedEmojiElementSettings
from .StackedIconElementSettings import StackedIconElementSettings

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
    LastUpdated: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=1900,Y=980,FillColor="#777",Anchor="e", Stroke=False, Format="Last Updated: %Y-%m-%d %I:%M:%S %p"))
    Observed: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=1900,Y=960,FillColor="#777",Anchor="e", Stroke=False, Format="Observed: %Y-%m-%d %I:%M:%S %p"))
    Source: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900,Y=940,FillColor="#777",Anchor="e", Stroke=False))
    DayOfWeek: FormattedTextElementSettings = field(default_factory=lambda: TextElementSettings(X=30,Y=30,FillColor="#FFF",FontSize=40,FontWeight="bold", Format="%A"))
    FullDate: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=30,Y=90,FillColor="#FFF",FontSize=40,FontWeight="bold",Format="%B %d, %Y"))
    Time: FormattedTextElementSettings = field(default_factory=lambda: FormattedTextElementSettings(X=400, Y=30,FillColor="#FFF",FontSize=90,FontWeight="bold",Format="%-I:%M %p"))
    Station: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1900, Y=920, FillColor="#777", Anchor="e", Stroke=False))
    CurrentTempEmoji: StackedEmojiElementSettings = field(default_factory=lambda: StackedEmojiElementSettings(Enabled=False, X=1880, Y=80, Anchor="center", FontSize=72, Stroke=False))
    CurrentTempIcon: StackedIconElementSettings = field(default_factory=lambda: StackedIconElementSettings(X=1780, Y=30, Anchor="center", FontSize=72, Stroke=False, Width=100, Height=100))
    CurrentTemp: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1750, Y=30, Anchor="ne", FontSize=72, FontWeight="bold"))
    FeelsLike: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1750, Y=160, Anchor="ne", FillColor="#BBB", FontWeight="bold", FontSize=40))
    TempHigh: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1500,Y=30,Anchor="ne", FillColor="red", FontWeight="bold", FontSize=46))
    TempLow: TextElementSettings = field(default_factory=lambda: TextElementSettings(X=1500,Y=90,Anchor="ne", FillColor="blue", FontWeight="bold", FontSize=46))
    WindIndicator: WindIndicatorSettings = field(default_factory=lambda: WindIndicatorSettings(X=1700, Y=350, Size=100))
    HumiditySquare: HumiditySquareSettings = field(default_factory=lambda: HumiditySquareSettings(X=1290, Y=280, Size=100))
    RainSquare: RainSquareSettings = field(default_factory=lambda: RainSquareSettings(X=1400, Y=280, Size=100))
    RainForecast: RainForecastSettings = field(default_factory=lambda: RainForecastSettings(X=30, Y=850))
    TemperatureGraph: TemperatureGraphSettings = field(default_factory=lambda: TemperatureGraphSettings(X=930, Y=80, Width=360, Height=130))