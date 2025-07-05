from datetime import datetime
import logging
from data.CurrentData import CurrentData
from data.ForecastData import ForecastData, MoonPhase
from data.SunData import SunData
from helpers.DateTimeHelpers import DateTimeHelpers

class WeatherHelpers:
    def GetWeatherEmoji(state: str, time: datetime, forecast:ForecastData, sunData:SunData) -> str:
        text = state.lower()
        Moon = forecast.Moon
        IsNight = WeatherHelpers.IsNight(sunData, time)
        IsSunset = WeatherHelpers.IsSunset(sunData, time)
        IsSunrise = WeatherHelpers.IsSunrise(sunData, time)

        if "thunder" in text:
            return {"Emoji": "⛈️", "Color": "#FFD700"}  # Gold
        if "rain" in text or "shower" in text or "drizzle" in text:
            return {"Emoji": "🌧️", "Color": "#1E90FF"}  # Dodger Blue
        if IsNight and Moon == MoonPhase.NewMoon:
            return {"Emoji": Moon.ToEmoji, "Color": "#222222"}  # Dark gray
        if IsNight and Moon == MoonPhase.FullMoon:
            return {"Emoji": Moon.ToEmoji, "Color": "#FFFFE0"}  # Light Yellow
        if IsNight and Moon == MoonPhase.WaxingCrescent:
            return {"Emoji": Moon.ToEmoji, "Color": "#CCCCCC"}
        if IsNight and Moon == MoonPhase.FirstQuarter:
            return {"Emoji": Moon.ToEmoji, "Color": "#DDDDDD"}
        if IsNight and Moon == MoonPhase.WaxingGibbous:
            return {"Emoji": Moon.ToEmoji, "Color": "#EEEEEE"}
        if IsNight and Moon == MoonPhase.WaningGibbous:
            return {"Emoji": Moon.ToEmoji, "Color": "#EEEEEE"}
        if IsNight and Moon == MoonPhase.LastQuarter:
            return {"Emoji": Moon.ToEmoji, "Color": "#DDDDDD"}
        if IsNight and Moon == MoonPhase.WaningCrescent:
            return {"Emoji": Moon.ToEmoji, "Color": "#CCCCCC"}
        if "sun" in text and "cloud" in text:
            return {"Emoji": "⛅", "Color": "#FFE066"}  # Light Yellow/Cloud mix
        if "partly" in text:
            return {"Emoji": "🌤️", "Color": "#FFD966"}  # Warm sunny
        if "sun" in text or "clear":
            return {"Emoji": "☀️", "Color": "#FFA500"}  # Orange
        if "cloud" in text or "overcast" in text:
            return {"Emoji": "☁️", "Color": "#B0C4DE"}  # LightSteelBlue
        if "snow" in text:
            return {"Emoji": "🌨️", "Color": "#ADD8E6"}  # Light Blue
        if "fog" in text or "mist" in text:
            return {"Emoji": "🌫️", "Color": "#C0C0C0"}  # Silver
        if IsSunrise:
            return {"Emoji": "🌅", "Color": "#FFA07A"}  # Light Salmon
        if IsSunset:
            return {"Emoji": "🌆", "Color": "#FF7F50"}  # Coral

        logging.debug(f"Could not parse '{state}' at '{time}' into a weather Emoji. Night: {IsNight}, Sunrise: {IsSunrise}, Sunset: {IsSunset}")
        return {"Emoji": "❓", "Color": "#FFFFFF"}  # Fallback to white

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