from datetime import datetime
import logging
from data.CurrentData import CurrentData
from data.ForecastData import ForecastData, MoonPhase
from data.SunData import SunData
from helpers.DateTimeHelpers import DateTimeHelpers

class WeatherHelpers:
    def IsNight(sunData:SunData, time:datetime):
        try:
            
            sunriseToday = sunData.Today.Sunrise.AstronomicalTwilight
            sunsetToday = sunData.Today.Sunset.AstronomicalTwilight

            sunriseTomorrow = sunData.Tomorrow.Sunrise.AstronomicalTwilight
            sunsetTomorrow = sunData.Tomorrow.Sunset.AstronomicalTwilight

            return (DateTimeHelpers.LessThan(time, sunriseToday)
                    or DateTimeHelpers.BetweenNotEqual(sunsetToday, time, sunriseTomorrow)
                    or DateTimeHelpers.LessThan(sunsetTomorrow, time))

        except Exception as e:
            logging.warning(f"is_night exception: {e}")
            return False

    def IsSunset(sunData:SunData, time:datetime):
        try:

            start = sunData.Today.Sunset.Start
            end = sunData.Today.Sunset.AstronomicalTwilight

            tomorrowstart = sunData.Tomorrow.Sunset.Start
            tomorrowend = sunData.Today.Sunset.AstronomicalTwilight

            return DateTimeHelpers.BetweenOrEqual(start, time, end) or DateTimeHelpers.BetweenOrEqual(tomorrowstart, time, tomorrowend)
        except Exception as e:
            logging.warning(f"Failed to determine sunset time: {e}")
            return False

    def IsSunrise(sunData:SunData, time:datetime):
        try:
            start = sunData.Today.Sunrise.AstronomicalTwilight
            end = sunData.Today.Sunrise.Day

            tomorrowstart = sunData.Tomorrow.Sunrise.AstronomicalTwilight
            tomorrowend = sunData.Tomorrow.Sunrise.Day

            return DateTimeHelpers.BetweenOrEqual(start, time, end) or DateTimeHelpers.BetweenOrEqual(tomorrowstart, time, tomorrowend)
        except:
            logging.warning(f"Failed to determine sunrise time: {e}")
            return False

    def ClassifyWeatherBackground(current:CurrentData, sunData:SunData):
        condition = current.get("State", "").lower()
        now = datetime.now()
        is_night = WeatherHelpers.IsNight(sunData, now)

        try:
            if WeatherHelpers.IsSunrise(sunData, now):
                return "Sunrise"
            elif WeatherHelpers.IsSunset(sunData, now):
                return "Sunset"
            elif WeatherHelpers.IsNight(sunData, now):
                return "Night"

        except Exception as e:
            logging.warning(f"Failed to classify sunrise/sunset window: {e}")

        # Weather-based conditions (fallbacks)
        if "rain" in condition or "shower" in condition:
            return "Rainy"
        if "sunny" in condition and not is_night:
            return "Sunny"
        if "partly" in condition or "mostly sunny" in condition:
            return "PartlyCloudy"
        if "cloud" in condition or "overcast" in condition:
            return "Cloudy"
        if is_night:
            return "Night"

        return "Cloudy"