from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
import math
from typing import Optional

@dataclass
class DailySunTimes:
    Sunrise: Optional[datetime] = None
    Sunset: Optional[datetime] = None
    SolarNoon: Optional[datetime] = None
    CivilTwilightBegin: Optional[datetime] = None
    CivilTwilightEnd: Optional[datetime] = None
    NauticalTwilightBegin: Optional[datetime] = None
    NauticalTwilightEnd: Optional[datetime] = None
    AstronomicalTwilightBegin: Optional[datetime] = None
    AstronomicalTwilightEnd: Optional[datetime] = None
    SolarNoon: Optional[datetime] = None
    Latitude: Optional[float] = None

    def getDegreesAboveHorizon(self, timePoint: datetime) -> float:
        if not self.SolarNoon or self.Latitude is None:
            return -90.0

        timePoint = timePoint.replace(tzinfo=None)
        dayOfYear = timePoint.timetuple().tm_yday

        declinationDegrees = -23.44 * math.cos(math.radians(360 / 365 * (dayOfYear + 10)))
        declinationRadians = math.radians(declinationDegrees)
        phiRadians = math.radians(self.Latitude)

        timeDiff = (timePoint - self.SolarNoon).total_seconds() / 3600
        hourAngleDegrees = 15 * timeDiff
        hourAngleRadians = math.radians(hourAngleDegrees)

        sinElevation = (math.sin(phiRadians) * math.sin(declinationRadians) +
                        math.cos(phiRadians) * math.cos(declinationRadians) * math.cos(hourAngleRadians))
        return math.degrees(math.asin(sinElevation))

    def findTimeForAngle(self, targetAngle: float, startTime: datetime, endTime: datetime, stepMinutes: int = 1) -> Optional[datetime]:
        current = startTime
        closestTime = None
        minDelta = float("inf")
        while current <= endTime:
            elevation = self.getDegreesAboveHorizon(current)
            delta = abs(elevation - targetAngle)
            if delta < minDelta:
                closestTime = current
                minDelta = delta
            current += timedelta(minutes=stepMinutes)
        return closestTime

    def GetNightEnd(self, date: datetime) -> Optional[datetime]:
        return self.findTimeForAngle(-18, datetime.combine(date, time(3, 0)), datetime.combine(date, time(8, 0)))

    def GetDayBegin(self, date: datetime) -> Optional[datetime]:
        return self.findTimeForAngle(6, datetime.combine(date, time(5, 0)), datetime.combine(date, time(10, 0)))

    def GetDayEnd(self, date: datetime) -> Optional[datetime]:
        return self.findTimeForAngle(6, datetime.combine(date, time(15, 0)), datetime.combine(date, time(20, 0)))

    def GetNightBegin(self, date: datetime) -> Optional[datetime]:
        return self.findTimeForAngle(-18, datetime.combine(date, time(17, 0)), datetime.combine(date, time(23, 59)))

class SunData:
    def __init__(self, yesterday:DailySunTimes, today:DailySunTimes, tomorrow:DailySunTimes, latitude: float):
        self.Yesterday = yesterday
        self.Today = today
        self.Tomorrow = tomorrow
        self.Latitude = latitude

    def GetDegreesAboveHorizon(self, time:datetime) -> float:
        time = time.replace(tzinfo=None)
        date = time.date()
        todayDate = datetime.now().date()

        if date == todayDate:
            solarNoon = self.Today.SolarNoon
        elif date == todayDate + timedelta(days = 1):
            solarNoon = self.Tomorrow.SolarNoon
        elif date == todayDate - timedelta(days = 1):
            solarNoon = self.Yesterday.SolarNoon
        else:
            return -90.0

        if not solarNoon:
            return -90.0

        dayOfYear = time.timetuple().tm_yday
        declinationDegrees = -23.44 * math.cos(math.radians(360 / 365 * (dayOfYear + 10)))
        declinationRadians = math.radians(declinationDegrees)

        phiRadians = math.radians(self.Latitude)

        timeDiff = (time - self.Today.SolarNoon).total_seconds() / 3600
        hourAngleDegrees = 15 * timeDiff
        hourAngleRadians = math.radians(hourAngleDegrees)

        sinElevation = (math.sin(phiRadians) * math.sin(declinationRadians) 
                        + math.cos(phiRadians) * math.cos(declinationRadians) * math.cos(hourAngleRadians))
        elevation = math.degrees(math.asin(sinElevation))

        return elevation

    def GetSkyColor(self, time: datetime) -> str:
        angle = self.GetDegreesAboveHorizon(time)

        gradient = [
            (-90, (11, 12, 42)),     # Deep night
            (-18, (25, 25, 112)),    # Astronomical twilight
            (-12, (128, 0, 128)),    # Nautical twilight
            (-6,  (255, 140, 66)),   # Civil twilight
            (0,   (255, 213, 128)),  # Sunrise/set
            (6,   (176, 216, 255)),  # Early day
            (20,  (135, 206, 235))   # Full day
        ]

        angle = max(gradient[0][0], min(angle, gradient[-1][0]))

        for i in range(len(gradient) - 1):
            a1, c1 = gradient[i]
            a2, c2 = gradient[i + 1]
            if a1 <= angle <= a2:
                ratio = (angle - a1) / (a2 - a1)
                r = int(c1[0] + (c2[0] - c1[0]) * ratio)
                g = int(c1[1] + (c2[1] - c1[1]) * ratio)
                b = int(c1[2] + (c2[2] - c1[2]) * ratio)
                return f"#{r:02x}{g:02x}{b:02x}"

        return "#000000"
