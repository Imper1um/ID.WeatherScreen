import logging
import requests
from dateutil import parser
from datetime import datetime, timedelta
from SunData import *
from WeatherConfig import WeatherConfig

class SunriseSunsetService:
    def __init__(self, config: WeatherConfig):
        self.Log = logging.getLogger("SunriseSunsetService")
        self.Config = config
        self.AstroTimesUrl = "https://api.sunrise-sunset.org/json"

    def GetSunData(self, latitude: float, longitude: float, date: datetime):
        return self.ParseSunData(self.QuerySunData(latitude, longitude, date), self.QuerySunData(latitude, longitude, date + timedelta(days = 1)))

    def ParseSunData(self, today, tomorrow):
        def to_local_naive(st):
            return parser.isoparse(st).astimezone().replace(tzinfo=None)

        todayData = today["results"]
        tomorrowData = tomorrow["results"]

        return SunData(
            Today=DailySunTimes(
                Sunrise=SunTimeSet(
                    AstronomicalTwilight=to_local_naive(todayData["astronomical_twilight_begin"]),
                    NauticalTwilight=to_local_naive(todayData["nautical_twilight_begin"]),
                    CivilTwilight=to_local_naive(todayData["civil_twilight_begin"]),
                    Day=to_local_naive(todayData["sunrise"])
                ),
                Sunset=SunsetSet(
                    Start=to_local_naive(todayData["sunset"]),
                    CivilTwilight=to_local_naive(todayData["civil_twilight_end"]),
                    NauticalTwilight=to_local_naive(todayData["nautical_twilight_end"]),
                    AstronomicalTwilight=to_local_naive(todayData["astronomical_twilight_end"])
                )
            ),
            Tomorrow=DailySunTimes(
                Sunrise=SunTimeSet(
                    AstronomicalTwilight=to_local_naive(tomorrowData["astronomical_twilight_begin"]),
                    NauticalTwilight=to_local_naive(tomorrowData["nautical_twilight_begin"]),
                    CivilTwilight=to_local_naive(tomorrowData["civil_twilight_begin"]),
                    Day=to_local_naive(tomorrowData["sunrise"])
                ),
                Sunset=SunsetSet(
                    Start=to_local_naive(tomorrowData["sunset"]),
                    CivilTwilight=to_local_naive(tomorrowData["civil_twilight_end"]),
                    NauticalTwilight=to_local_naive(tomorrowData["nautical_twilight_end"]),
                    AstronomicalTwilight=to_local_naive(tomorrowData["astronomical_twilight_end"])
                )
            )
        )

    def QuerySunData(self, latitude: float, longitude: float, date: datetime):
        params = {
            "lat": latitude,
            "lng": longitude,
            "date": date.strftime("%Y%m%d"),
            "formatted": 0
        }
        response = requests.get(self.AstroTimesUrl, params=params)
        response.raise_for_status()
        return response.json()