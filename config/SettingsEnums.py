from enum import Enum

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