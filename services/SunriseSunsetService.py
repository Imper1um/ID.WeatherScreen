import logging, requests

from dateutil import parser
from datetime import datetime, timedelta

from config.WeatherConfig import WeatherConfig

from data.SunData import *

class SunriseSunsetService:
    def __init__(self, config: WeatherConfig):
        self.Log = logging.getLogger("SunriseSunsetService")
        self.Config = config
        self.AstroTimesUrl = "https://api.sunrise-sunset.org/json"
        self.DailyCache = {}

    def GetSunData(self, latitude: float, longitude: float, date: datetime) -> SunData:
        yesterday = self.QuerySunData(latitude, longitude, date - timedelta(days=1))
        today = self.QuerySunData(latitude, longitude, date)
        tomorrow = self.QuerySunData(latitude, longitude, date + timedelta(days=1))

        return SunData(
            today=today,
            tomorrow=tomorrow,
            yesterday=yesterday,
            latitude=latitude
        )

    def QuerySunData(self, latitude: float, longitude: float, date: datetime) -> DailySunTimes:
        date_str = date.strftime("%Y%m%d")
        key = (date_str, round(latitude, 3), round(longitude, 3))

        if key in self.DailyCache:
            return self.DailyCache[key]

        localTimezone = datetime.now().astimezone().tzinfo
        tzid = getattr(localTimezone, "key", None) or str(localTimezone)
        params = {
            "lat": latitude,
            "lng": longitude,
            "date": date_str,
            "formatted": 0,
            "tzid": tzid
        }
        response = requests.get(self.AstroTimesUrl, params=params)
        response.raise_for_status()
        results = response.json()["results"]

        def to_local_naive(st):
            return parser.isoparse(st).astimezone().replace(tzinfo=None)

        sunTimes = DailySunTimes(
            Sunrise=to_local_naive(results["sunrise"]),
            Sunset=to_local_naive(results["sunset"]),
            SolarNoon=to_local_naive(results["solar_noon"]),
            CivilTwilightBegin=to_local_naive(results["civil_twilight_begin"]),
            CivilTwilightEnd=to_local_naive(results["civil_twilight_end"]),
            NauticalTwilightBegin=to_local_naive(results["nautical_twilight_begin"]),
            NauticalTwilightEnd=to_local_naive(results["nautical_twilight_end"]),
            AstronomicalTwilightBegin=to_local_naive(results["astronomical_twilight_begin"]),
            AstronomicalTwilightEnd=to_local_naive(results["astronomical_twilight_end"]),
        )

        self.DailyCache[key] = sunTimes
        return sunTimes
