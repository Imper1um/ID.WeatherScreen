from datetime import datetime
from data.EmojiDisplay import EmojiDisplay
from data.MoonPhase import MoonPhase
from config.IconType import IconType
from data.IconDisplay import IconDisplay

class WeatherConditions:
    def __init__(self, 
                 time:datetime,                        # Local Time
                 rainRate:float = None,                # In Inches
                 snowRate:float = None,                # In Inches
                 cloudCover: float = None,             # In Percentage (0.0-1.0)
                 moonPhase: MoonPhase = None,
                 windGust:float = None,                # In MPH
                 windSpeed: float = None,              # In MPH
                 visibility: float = None,             # In Miles
                 sunAngle: float = None,               # In Degrees above the horizon
                 isLightning:bool = False,
                 isFoggy:bool = False,
                 isFreezing:bool = False,
                 isHail:bool = False,
                 isWarning:bool = False,               # Is there some kind of extreme weather warning?
                 isHurricane:bool = False,
                 stateConditions:str = ""):
        self.RainRate = rainRate
        self.SnowRate = snowRate
        self.CloudCover = cloudCover
        self.Moon = moonPhase
        self.WindGust = windGust
        self.WindSpeed = windSpeed
        self.Visibility = visibility
        self.SunAngle = sunAngle
        self.IsLightning = isLightning
        self.IsFoggy = isFoggy
        self.IsFreezing = isFreezing
        self.IsHail = isHail
        self.IsWarning = isWarning
        self.IsHurricane = isHurricane
        self.StateConditions = stateConditions
        self.Time = time

    def GetEmoji(self) -> EmojiDisplay:
        sun = self.SunAngle
        isNight = sun < -18
        isAstronomicalTwilight = -18 <= sun < -12
        isNauticalTwilight = -12 <= sun < -6
        isCivilTwilight = -6 <= sun < 0
        isDay = sun >= 0
        isFullDay = sun > 6

        background = "🌅"
        if self.IsHurricane:
            return EmojiDisplay(Back="🌀", Front="⚠")
        if isNight:
            background = self.Moon.ToEmoji if self.Moon is not None else "🌕"
        elif isAstronomicalTwilight or isNauticalTwilight:
            background = "🌌"
        elif isCivilTwilight:
            background = "🌆"
        elif isDay or isFullDay:
            background = "☀"
        
        if self.IsFoggy and self.IsLightning:
            return EmojiDisplay(Front="⚡", Middle="🌫", Back="⚠" if self.IsWarning else "")

        if self.IsWarning and self.IsLightning and self.RainRate > 0:
            return EmojiDisplay(Front="⛈", Back="⚠")
        if self.IsWarning and self.IsLightning and self.SnowRate > 0:
            return EmojiDisplay(Front="⚡", Middle="🌨", Back="⚠")
        if self.IsLightning and self.RainRate > 0:
            return EmojiDisplay(Back="⛈")
        if self.IsLightning and self.CloudCover > 0.8:
            return EmojiDisplay(Back="🌩")
        if self.IsLightning and self.CloudCover > 0.4:
            return EmojiDisplay(Back=background,Middle="🌩",Front="❄" if self.SnowRate > 0 else "")
        if self.IsLightning:
            return EmojiDisplay(Back=background,Middle="❄" if self.SnowRate > 0 else "",Front="⚡")

        if self.RainRate > 0 and self.CloudCover > 0.8:
            return EmojiDisplay(Front="❄" if self.IsFreezing else "",Middle="🌧", Back="⚠" if self.IsWarning else "")
        if self.SnowRate > 0 and self.CloudCover > 0.8:
            return EmojiDisplay(Front="❄" if self.IsFreezing else "",Middle="🌨", Back="⚠" if self.IsWarning else "")
        if self.IsHail and self.CloudCover > 0.8:
            return EmojiDisplay(Front="❄" if self.IsFreezing else "", Middle="🧊", Back="☁")

        if self.CloudCover > 0.8 and self.WindGust > 15:
            return EmojiDisplay(Back="☁", Front="🌬")
        if self.CloudCover > 0.8:
            return EmojiDisplay(Back="☁")
        if self.CloudCover > 0.4:
            return EmojiDisplay(Back=background, Middle="☁")
        if self.WindGust > 15:
            return EmojiDisplay(back=background, Middle="🌬")
        if self.IsFreezing:
            return EmojiDisplay(back=background, Middle="🧊")

        return EmojiDisplay(Back=background)

    def GetTimingTag(self) -> str:
        if self.SunAngle < -18:
            return "Night"
        if self.SunAngle > 6:
            return "Daylight"
        if self.Time.strftime("%p") == "AM":
            return "Sunrise"
        if self.Time.strftime("%p") == "PM":
            return "Sunset"

        return ""

    def GetWeatherTag(self) -> str:
        if self.IsHurricane:
            return "Lightning"
        
        if self.IsFoggy and self.IsLightning:
            return "Foggy"
        if self.IsLightning:
            return "Lightning"

        if self.SnowRate is not None and self.SnowRate > 0:
            return "Snow"
        if self.RainRate is not None:
            if self.RainRate > 4 or self.IsHail:
                return "HeavyRain"
            if self.RainRate > 1:
                return "MediumRain"
            if self.RainRate > 0:
                return "LightRain"

        if self.CloudCover is not None:
            if self.CloudCover > 0.8 and self.WindGust > 15:
                return "Windy"
            if self.CloudCover > 0.8:
                return "Cloudy"
            if self.CloudCover > 0.4:
                return "PartlyCloudy"
        if self.WindGust > 15:
            return "Windy"
        if self.IsFreezing:
            return "Snow"

        return "Clear"

    def GetIcon(self) -> IconDisplay:
        icon = IconType.Unknown
        front = None
        middle = None

        if self.IsHurricane and self.WindGust is not None and self.WindGust < 45:
            return IconDisplay(Icon = IconType.Light_Hurricane)
        if self.IsHurricane:
            return IconDisplay(Icon = IconType.Danger_Hurricane)

        if self.IsWarning and self.IsLightning:
            return IconDisplay(Icon=IconType.Alert_Thunderstorm, Middle = "🧊" if self.IsFreezing else "")

        if self.IsLightning and self.RainRate is not None and self.RainRate > 0:
            return IconDisplay(Icon=IconType.Thunderstorm, Middle = "🧊" if self.IsFreezing else "")
        if self.IsLightning:
            return IconDisplay(Icon=IconType.Lightning, Middle = "🧊" if self.IsFreezing else "")

        if self.SnowRate is not None and self.SnowRate > 4:
            return IconDisplay(Icon=IconType.Heavy_Snow)
        if self.SnowRate is not None and self.SnowRate > 1:
            return IconDisplay(Icon=IconType.Moderate_Snow)
        if self.SnowRate is not None and self.SnowRate > 0:
            return IconDisplay(Icon=IconType.Light_Snow)

        if self.RainRate is not None and self.RainRate > 0.5:
            return IconDisplay(Icon=IconType.Heavy_Rain, Middle = "🧊" if self.IsFreezing else "")
        if self.RainRate is not None and self.RainRate > 0.2:
            return IconDisplay(Icon=IconType.Moderate_Rain, Middle = "🧊" if self.IsFreezing else "")
        if self.RainRate is not None and self.RainRate > 0:
            return IconDisplay(Icon=IconType.Light_Rain, Middle = "🧊" if self.IsFreezing else "")

        if self.IsFoggy and self.Visibility < 1:
            return IconDisplay(Icon=IconType.Mist, Middle = "🧊" if self.IsFreezing else "")
        if self.IsFoggy:
            return IconDisplay(Icon=IconType.Foggy, Middle = "🧊" if self.IsFreezing else "")

        if self.IsHail:
            return IconDisplay(Icon=IconType.Cloudy, Middle="🔻", Front="🧊")

        if ((self.RainRate is not None and self.RainRate > 0) or (self.SnowRate is not None and self.SnowRate > 0)) and self.CloudCover is not None and self.CloudCover < 0.6 and self.SunAngle > -18:
            return IconDisplay(Icon=IconType.Patchy_Rain, Middle = "🧊" if self.IsFreezing else "")

        if self.CloudCover is not None and self.CloudCover > 0.85:
            return IconDisplay(Icon=IconType.Overcast, Middle = "🧊" if self.IsFreezing else "")
        if self.CloudCover is not None and self.CloudCover > 0.5:
            return IconDisplay(Icon=IconType.Cloudy, Middle = "🧊" if self.IsFreezing else "")
        if self.CloudCover is not None and self.CloudCover > 0.2 and self.SunAngle > -16:
            return IconDisplay(Icon=IconType.Partly_Cloudy, Middle = "🧊" if self.IsFreezing else "")

        if self.SunAngle > 6:
            return IconDisplay(Icon=IconType.Sunny)

        if self.SunAngle < -18:
            icon = IconType.New_Moon
            if self.Moon == MoonPhase.FirstQuarter:
                icon = IconType.First_Quarter
            elif self.Moon == MoonPhase.FullMoon:
                icon = IconType.Full_Moon
            elif self.Moon == MoonPhase.LastQuarter:
                icon = IconType.Last_Quarter
            elif self.Moon == MoonPhase.WaningCrescent:
                icon = IconType.Waning_Crescent
            elif self.Moon == MoonPhase.WaningGibbous:
                icon = IconType.Waning_Gibbous
            elif self.Moon == MoonPhase.WaxingCrescent:
                icon = IconType.Waxing_Crescent
            elif self.Moon == MoonPhase.WaxingGibbous:
                icon = IconType.Waxing_Gibbous
            
            return IconDisplay(Icon=icon, Middle = "🧊" if self.IsFreezing else "")

        return IconDisplay(Icon=IconType.Unknown)
